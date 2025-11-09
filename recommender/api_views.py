from django.http import JsonResponse
from django.db.models import Count
from crmapp.models import ServiceProduct, customer_details, TaxInvoice, TaxInvoiceItem

from django.views.decorators.csrf import csrf_exempt
import json
# ==================================================
# 🌐 RECOMMENDER SYSTEM API ENDPOINTS
# ==================================================

# 1️⃣ Content-Based Recommendation
def get_recommendations(request):
    product_name = request.GET.get('product', '').strip()
    if not product_name:
        return JsonResponse({'error': 'Please provide a product name.'}, status=400)

    # 🧠 Filter by product__name instead of name
    product = ServiceProduct.objects.filter(product__name__icontains=product_name).first()
    if not product:
        return JsonResponse({'error': 'Product not found.'}, status=404)

    similar_products = ServiceProduct.objects.filter(
        service=product.service
    ).exclude(id=product.id)[:5]

    return JsonResponse({
        'base_product': product.product.name,
        'recommended_products': [p.product.name for p in similar_products]
    })


# 2️⃣ Collaborative Filtering Recommendation
def collaborative_recommendations(request, customer_id):
    customer_invoices = TaxInvoice.objects.filter(customer_id=customer_id)
    if not customer_invoices.exists():
        return JsonResponse({'error': 'No purchases found for this customer.'}, status=404)

    purchased_products = TaxInvoiceItem.objects.filter(
        invoice__in=customer_invoices
    ).values_list('product_id', flat=True)

    similar_invoices = TaxInvoiceItem.objects.filter(
        product_id__in=purchased_products
    ).exclude(invoice__customer_id=customer_id)

    similar_customers = TaxInvoice.objects.filter(
        id__in=similar_invoices.values_list('invoice_id', flat=True)
    ).values('customer_id').annotate(common_count=Count('customer_id')).order_by('-common_count')

    return JsonResponse({'similar_customers': list(similar_customers)})


# 3️⃣ Upselling Recommendations
def upsell_recommendations_api(request, product_id):
    try:
        base_product = ServiceProduct.objects.get(id=product_id)
    except ServiceProduct.DoesNotExist:
        return JsonResponse({'error': 'Product not found.'}, status=404)

    upsell_products = ServiceProduct.objects.filter(
        service=base_product.service,
        price__gt=base_product.price
    ).order_by('price')[:3]

    return JsonResponse({
        'product': base_product.product.name,
        'upsell_suggestions': [p.product.name for p in upsell_products]
    })


# 4️⃣ Cross-Selling Recommendations
def cross_sell_recommendations_api(request, customer_id):
    invoices = TaxInvoice.objects.filter(customer_id=customer_id)
    if not invoices.exists():
        return JsonResponse({'error': 'No purchases found for this customer.'}, status=404)

    purchased_products = TaxInvoiceItem.objects.filter(
        invoice__in=invoices
    ).values_list('product_id', flat=True)

    co_purchased = (
        TaxInvoiceItem.objects
        .filter(invoice__in=invoices)
        .exclude(product_id__in=purchased_products)
        .values('product__name')
        .annotate(count=Count('product'))
        .order_by('-count')[:5]
    )

    return JsonResponse({
        'cross_sell_suggestions': list(co_purchased)
    })


@csrf_exempt
def generate_message_view(request):
    """AI Auto Message Generator"""
    if request.method == "POST":
        data = json.loads(request.body)
        customer = data.get("customer_name")
        base = data.get("base_product")
        recommended = data.get("recommended_product")
        rec_type = data.get("recommendation_type")

        message = f"Hi {customer}, since you purchased {base}, you might love {recommended}! (Type: {rec_type})"
        return JsonResponse({"message": message})

@csrf_exempt
def send_message_view(request):
    """Send message endpoint"""
    if request.method == "POST":
        data = json.loads(request.body)
        return JsonResponse({"message": f"✅ Message sent to {data.get('customer_name')} successfully!"})