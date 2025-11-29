# recommender/api_views.py
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from recommender.models import Item
from crmapp.models import customer_details, TaxInvoice, TaxInvoiceItem
import json
import requests

# RAP BOOSTER settings
RAPBOOSTER_API_KEY = "6538c8eff027d41e9151"
RAPBOOSTER_API_URL = "https://rapbooster.in/api/send"


# -------------------------
# Product list for UI
# -------------------------
def product_list(request):
    products = list(Item.objects.order_by("title").values_list("title", flat=True))
    return JsonResponse({"products": products})


# -------------------------
# Customers list for UI
# -------------------------
def customer_list(request):
    # returns list of { customer_id, customer_name }
    qs = customer_details.objects.all().values("id", "fullname")
    data = [{"customer_id": c["id"], "customer_name": c["fullname"]} for c in qs]
    return JsonResponse({"customers": data})


# -------------------------
# Customer detail / phone
# -------------------------
def customer_phone(request, cid):
    try:
        c = customer_details.objects.get(id=cid)
    except customer_details.DoesNotExist:
        return JsonResponse({"error": "Customer not found."}, status=404)

    # Try primarycontact then secondarycontact
    phone = None
    if hasattr(c, "primarycontact") and c.primarycontact:
        phone = str(c.primarycontact)
    elif hasattr(c, "secondarycontact") and c.secondarycontact:
        phone = str(c.secondarycontact)

    return JsonResponse({
        "customer_id": c.id,
        "customer_name": getattr(c, "fullname", ""),
        "phone": phone
    })


# -------------------------
# Content-based recommendations
# -------------------------
def get_recommendations(request):
    product_name = request.GET.get("product", "").strip()
    if not product_name:
        return JsonResponse({"error": "Please provide a product name."}, status=400)

    product = Item.objects.filter(title__icontains=product_name).first()
    if not product:
        return JsonResponse({"error": "Product not found."}, status=404)

    similar_products = Item.objects.filter(category=product.category).exclude(id=product.id)[:6]
    return JsonResponse({
        "base_product": product.title,
        "recommended_products": [p.title for p in similar_products]
    })


# -------------------------
# Personalized / Collaborative recommendations (for customer)
# Returns {"recommendations": ["Product A", "Product B", ...]}
# -------------------------
def user_recommendations(request, customer_id):
    invoices = TaxInvoice.objects.filter(customer_id=customer_id)
    if not invoices.exists():
        return JsonResponse({"recommendations": []})

    # products this customer purchased
    purchased_product_ids = TaxInvoiceItem.objects.filter(invoice__in=invoices).values_list("product_id", flat=True)

    # Find other invoice items co-purchased by other customers (excluding customer's products)
    co_purchased = (TaxInvoiceItem.objects
                    .exclude(product_id__in=purchased_product_ids)
                    .values("product_id")
                    .annotate(cnt=Count("product_id"))
                    .order_by("-cnt")[:8])

    # Map product_id -> product title using Item model (best effort)
    product_titles = []
    for entry in co_purchased:
        pid = entry["product_id"]
        item = Item.objects.filter(id=pid).first()
        if item:
            product_titles.append(item.title)
        else:
            # fallback to product_id string if no Item row
            product_titles.append(f"Product-{pid}")

    return JsonResponse({"recommendations": product_titles})


# -------------------------
# Upsell suggestions (by product_id)
# -------------------------
def upsell_recommendations_api(request, product_id):
    try:
        base = Item.objects.get(id=product_id)
    except Item.DoesNotExist:
        return JsonResponse({'error': 'Product not found.'}, status=404)

    # Suggest higher-tier (recent) products in same category
    upsells = Item.objects.filter(category=base.category).exclude(id=base.id).order_by("-created_at")[:4]
    return JsonResponse({"product": base.title, "upsell_suggestions": [p.title for p in upsells]})


# -------------------------
# Cross-sell suggestions (by customer)
# -------------------------
def cross_sell_recommendations_api(request, customer_id):
    invoices = TaxInvoice.objects.filter(customer_id=customer_id)
    if not invoices.exists():
        return JsonResponse({'cross_sell_suggestions': []})

    purchased_product_ids = TaxInvoiceItem.objects.filter(invoice__in=invoices).values_list("product_id", flat=True)

    co_purchased = (TaxInvoiceItem.objects
                    .exclude(product_id__in=purchased_product_ids)
                    .values("product_id")
                    .annotate(cnt=Count("product_id"))
                    .order_by("-cnt")[:6])

    titles = []
    for entry in co_purchased:
        pid = entry["product_id"]
        item = Item.objects.filter(id=pid).first()
        if item:
            titles.append(item.title)
        else:
            titles.append(f"Product-{pid}")

    return JsonResponse({"cross_sell_suggestions": titles})


# -------------------------
# Message generation (simple)
# -------------------------
@csrf_exempt
def generate_message_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)
    try:
        data = json.loads(request.body)
        customer = data.get("customer_name")
        base = data.get("base_product")
        recommended = data.get("recommended_product")
        rec_type = data.get("recommendation_type", "recommendation")
        if not all([customer, base, recommended]):
            return JsonResponse({"error": "Missing required fields."}, status=400)

        message = f"Hello {customer}, since you had {base}, we recommend {recommended}. ({rec_type})"
        return JsonResponse({"message": message})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# -------------------------
# Send message via RAP Booster
# -------------------------
@csrf_exempt
def send_message_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        customer_name = data.get("customer_name")
        customer_number = data.get("customer_number")
        message = data.get("message")

        if not all([customer_name, customer_number, message]):
            return JsonResponse({"error": "customer_name, customer_number, message required."}, status=400)

        payload = {
            "apikey": RAPBOOSTER_API_KEY,
            "mobile": str(customer_number),
            "msg": message
        }

        response = requests.post(RAPBOOSTER_API_URL, data=payload, timeout=15)
        try:
            result = response.json() if response.text else {"status": "no response"}
        except:
            result = {"status": "invalid json from provider", "text": response.text}

        if response.status_code == 200:
            return JsonResponse({"status": "success", "response": result})
        else:
            return JsonResponse({"status": "failed", "response": result}, status=500)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
