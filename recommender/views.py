# recommender/views.py

from django.shortcuts import render
from django.db import connection
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
import json
import pickle
import os
import requests
import re

# Models
from crmapp.models import MessageTemplates, Product, customer_details
from .models import SentMessageLog, Item, Rating, PestRecommendation

# Recommender Engine
from .recommender_engine import (
    get_content_based_recommendations,
    get_collaborative_recommendations,
    get_upsell_recommendations,
    get_crosssell_recommendations,
    generate_recommendations_for_user,
    get_user_based_recommendations
)

from .utils import send_recommendation_message

# Helper: Render placeholders
def render_template(text, data):
    return re.sub(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}", lambda m: str(data.get(m.group(1), "")), text or "")

# ============================================================
# 1️⃣ RECOMMENDATION UI
# ============================================================
def recommendation_ui(request):
    customers = customer_details.objects.all().values("id", "fullname")
    templates = MessageTemplates.objects.filter(is_active=True).order_by("category", "message_type")
    
    selected_product_id = request.GET.get("product_id")
    customer_id = request.GET.get("customer_id")

    customer = None
    product = None
    
    if selected_product_id:
        try:
            product = Product.objects.get(id=selected_product_id)
        except Product.DoesNotExist:
            pass
    
    if customer_id:
        try:
            customer = customer_details.objects.get(id=customer_id)
            if getattr(customer, 'lead_status', None):
                templates = MessageTemplates.objects.filter(
                    category='lead', 
                    lead_status=customer.lead_status, 
                    is_active=True
                ).order_by("message_type")
            else:
                templates = MessageTemplates.objects.filter(
                    category='lead', 
                    is_active=True
                ).order_by("message_type")
        except customer_details.DoesNotExist:
            pass
    
    return render(request, 'recommender/recommendations_ui.html', {
        'templates': templates,
        'customer': customer,
        'product': product,
        'customers': customers,
    })

# ============================================================
# 2️⃣ CONTENT-BASED RECOMMENDATIONS (product → product)
# ============================================================
def recommendations_view(request):
    product_name = request.GET.get('product')
    if not product_name:
        return JsonResponse({'error': 'Please provide a product name.'}, status=400)
    try:
        results = get_content_based_recommendations(product_name)
        return JsonResponse({'recommended_products': results})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ============================================================
# 3️⃣ COLLABORATIVE FILTERING (customer → customer)
# ============================================================
def collaborative_view(request, customer_id):
    try:
        results = get_collaborative_recommendations(customer_id)
        return JsonResponse({'similar_customers': results})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ============================================================
# 4️⃣ UPSELL (product → higher product)
# ============================================================
def upsell_view(request, product_id):
    try:
        results = get_upsell_recommendations(product_id)
        return JsonResponse({'upsell_suggestions': results})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ============================================================
# 5️⃣ CROSS-SELL (customer → new related products)
# ============================================================
def crosssell_view(request, customer_id):
    try:
        results = get_crosssell_recommendations(customer_id)
        return JsonResponse({'cross_sell_suggestions': results})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ============================================================
# 6️⃣ DASHBOARD TABLE (CRM)
# ============================================================
def recommendation_dashboard(request):
    try:
        filter_type = (request.GET.get("type") or "").strip()
        search = request.GET.get("search", "").strip()
        sort_column = request.GET.get("sort", "confidence_score")
        sort_order = request.GET.get("order", "desc")

        # Allowed sorting fields
        valid_columns = {
            "customer_name": "c.fullname",
            "base_product": "bp.product_name",
            "recommended_product": "rp.product_name",
            "recommendation_type": "pr.recommendation_type",
            "confidence_score": "pr.confidence_score",
        }
        sort_field = valid_columns.get(sort_column, "pr.confidence_score")
        order_sql = "DESC" if sort_order == "desc" else "ASC"

        # Base SQL
        sql = """
            SELECT 
                c.fullname AS customer_name,
                c.primarycontact AS phone_number,
                bp.product_name AS base_product,
                bp.category AS base_product_category,
                rp.product_name AS recommended_product,
                rp.category AS recommended_product_category,
                pr.recommendation_type,
                pr.confidence_score
            FROM pest_recommendations pr
            LEFT JOIN crmapp_customer_details c ON pr.customer_id = c.id
            LEFT JOIN crmapp_product bp ON pr.base_product_id = bp.product_id
            LEFT JOIN crmapp_product rp ON pr.recommended_product_id = rp.product_id
            WHERE 1=1
        """

        params = []

        # 🔥 Filter recommendation type (case-insensitive)
        # Handles: "upsell", "UpSell", "up sell", "UP_SELL", etc.
        if filter_type:
            sql += " AND LOWER(pr.recommendation_type) LIKE %s"
            params.append(f"%{filter_type.lower()}%")

        # 🔍 Search (customer or products)
        if search:
            sql += """
                AND (
                    c.fullname LIKE %s OR
                    bp.product_name LIKE %s OR
                    rp.product_name LIKE %s
                )
            """
            params.extend([f"%{search}%"] * 3)

        # Sorting
        sql += f" ORDER BY {sort_field} {order_sql};"

        # Fetch data
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            rows = cursor.fetchall()

        data = []
        for row in rows:
            data.append({
                "customer_name": row[0],
                "phone_number": str(row[1]) if row[1] else None,
                "base_product": row[2],
                "base_product_category": row[3],
                "recommended_product": row[4],
                "recommended_product_category": row[5],
                "recommendation_type": row[6],
                "confidence_score": float(row[7]) if row[7] is not None else None,
            })

        # Pagination
        page_obj = Paginator(data, 10).get_page(request.GET.get("page"))

        return render(request, "recommender/recommendation_dashboard.html", {
            "recommendations": page_obj.object_list,
            "page_obj": page_obj,
            "sort": sort_column,
            "order": sort_order,
            "filter_type": filter_type,
            "search": search,
        })

    except Exception as e:
        return render(request, "recommender/recommendation_dashboard.html", {
            "recommendations": [],
            "error": str(e)
        })


# ============================================================
# 7️⃣ GET ALL PRODUCTS
# ============================================================
def get_all_products(request):
    try:
        products = list(Product.objects.values_list("product_name", flat=True))
        return JsonResponse({'products': products})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ============================================================
# 8️⃣ AI-Powered Personalized Recommendations
# ============================================================
import logging
from django.shortcuts import get_object_or_404
from .recommender_engine import generate_recommendations_for_user
logger = logging.getLogger(__name__)

@csrf_exempt
@login_required
def api_ai_personalized(request, customer_id):
    try:
        # Validate and fetch customer safely
        customer_id = int(customer_id)  # Ensure it's an integer
        customer = get_object_or_404(customer_details, id=customer_id)
        
        # Generate recommendations with error handling
        try:
            recommendations = generate_recommendations_for_user(customer_id=customer_id, top_n=5)
        except Exception as e:
            logger.error(f"Error generating recommendations for customer {customer_id}: {str(e)}")
            recommendations = Item.objects.none()  # Fallback to empty queryset
        
        # Process recommendations into a consistent format
        results = []
        for r in recommendations:
            try:
                if isinstance(r, Item):
                    # Use Item fields directly; product_id is the ForeignKey value
                    results.append({
                        "product_id": r.product_id,  # ID of the related Product
                        "title": r.title,
                        "category": r.category,
                        "tags": r.tags,
                        "confidence_score": getattr(r, "score", None),  # Attached in engine
                    })
                elif hasattr(r, 'id'):  # For Product or other models (fallback)
                    results.append({
                        "product_id": r.id,
                        "title": getattr(r, "product_name", str(r)),  # Assuming Product has product_name
                        "category": getattr(r, "category", None),
                        "tags": getattr(r, "tags", ""),
                        "confidence_score": getattr(r, "score", None),
                    })
                else:
                    # Generic fallback for unexpected types
                    results.append({
                        "product_id": getattr(r, "id", None),
                        "title": getattr(r, "title", str(r)),
                        "category": getattr(r, "category", None),
                        "tags": getattr(r, "tags", None),
                        "confidence_score": getattr(r, "score", None),
                    })
            except Exception as e:
                logger.warning(f"Error processing recommendation item for customer {customer_id}: {str(e)}")
                continue  # Skip malformed items
        
        # Always return a successful response
        return JsonResponse({
            "customer_id": customer.id,
            "customer_name": customer.fullname,
            "recommendations": results,  # Empty list if none
        })
    
    except customer_details.DoesNotExist:
        logger.error(f"Customer with ID {customer_id} not found.")
        return JsonResponse({"error": "Customer not found"}, status=404)
    except ValueError:
        logger.error(f"Invalid customer ID: {customer_id}")
        return JsonResponse({"error": "Invalid customer ID"}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in api_ai_personalized for customer {customer_id}: {str(e)}")
        return JsonResponse({"error": "Internal server error"}, status=500)

# ============================================================
# 9️⃣ AUTOMATIC MESSAGE GENERATION + SEND
# ============================================================
@csrf_exempt
def generate_message(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)
    try:
        data = json.loads(request.body)
        customer = data.get("customer_name")
        base = data.get("base_product")
        rec = data.get("recommended_product")
        rec_type = data.get("recommendation_type")
        phone_number = data.get("phone_number")

        if not all([customer, base, rec, rec_type, phone_number]):
            return JsonResponse({"error": "Missing fields"}, status=400)

        message = (
            f"Hello {customer}, we recommend trying our {rec} as a perfect "
            f"{rec_type.lower()} option with your {base}. "
            f"It ensures better pest control results! 🌾🛡️"
        )

        status_code, api_response = send_recommendation_message(
            phone_number=phone_number,
            message=message,
            customer_name=customer
        )

        return JsonResponse({
            "customer": customer,
            "phone": phone_number,
            "message": message,
            "status": "sent" if status_code == 200 else "failed",
            "api_response": api_response
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# ============================================================
# 🔟 RAP BOOSTER MESSAGE SENDER
# ============================================================ 
import os
import requests
import logging
from django.core.exceptions import ValidationError

# ... (keep your existing imports at the top of the file; remove any duplicates)

# Remove these lines from the module level (they're causing the crash):
# RAPBOOSTER_API_KEY = os.getenv('6538c8eff027d41e9151')  # This is wrong
# if not RAPBOOSTER_API_KEY:
#     raise ValueError("RAPBOOSTER_API_KEY environment variable not set")
# RAPBOOSTER_SEND_URL = "https://api.rapbooster.com/v1/send"

# Set up logging (keep this if not already present)
logger = logging.getLogger(__name__)

@csrf_exempt
def send_message_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)
    
    try:
        # Load API key securely (prefer env var; fallback to hardcoded for testing only)
        RAPBOOSTER_API_KEY = os.getenv('RAPBOOSTER_API_KEY') or '6538c8eff027d41e9151'  # Remove hardcoded fallback in production!
        if not RAPBOOSTER_API_KEY:
            return JsonResponse({"status": "failed", "error": "API key not configured"}, status=500)
        
        RAPBOOSTER_SEND_URL = "https://api.rapbooster.com/v1/send"  # Confirm exact URL in docs
        
        data = json.loads(request.body)
        template_id = data.get("template_id")
        customer_id = data.get("customer_id")
        
        if not template_id or not customer_id:
            return JsonResponse({"error": "template_id and customer_id are required"}, status=400)
        
        template = MessageTemplates.objects.get(id=template_id)
        customer = customer_details.objects.get(id=customer_id)
        
        # Basic validation
        phone = customer.primarycontact
        if not phone or not re.match(r'^\+?\d{10,15}$', str(phone)):  # Simple phone regex; adjust as needed
            return JsonResponse({"error": "Invalid phone number"}, status=400)
        
        rendered_body = render_template(template.body, {
            'customer_name': customer.fullname,
            'recommended_product': data.get('recommended_product', ''),
        })
        
        # Updated payload based on your guide (confirm with RapBooster docs)
        payload = {
            "apikey": RAPBOOSTER_API_KEY,
            "phone": str(phone),  # Ensure it's a string
            "message": rendered_body
        }
        
        # Make the API call with timeout
        response = requests.post(RAPBOOSTER_SEND_URL, json=payload, timeout=10)
        response_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
        
        # Log the full response for debugging/verification
        logger.info(f"RapBooster API Response: {response.text}")
        
        # Check for actual success (not just HTTP 200)
        is_success = (
            response.status_code == 200 and
            response_data.get('status') == 'success' and
            'message_id' in response_data  # Optional: Ensure a message ID was returned
        )
        
        status = "success" if is_success else "failed"
        error_details = response_data.get('error', 'Unknown error') if not is_success else None
        
        # Log to your model
        SentMessageLog.objects.create(
            template=template,
            recipient=phone,
            channel=template.message_type,
            rendered_body=rendered_body,
            status=status,
            provider_response=response.text  # Store full response for later inspection
        )
        
        # Return detailed response
        if is_success:
            return JsonResponse({
                "status": "success",
                "message_id": response_data.get('message_id'),
                "phone": response_data.get('phone'),
                "queue_status": response_data.get('queue_status')
            })
        else:
            return JsonResponse({
                "status": "failed",
                "error": error_details,
                "http_status": response.status_code
            }, status=response.status_code)
    
    except requests.RequestException as e:
        logger.error(f"Network error sending message: {str(e)}")
        return JsonResponse({"status": "failed", "error": "Network error"}, status=500)
    except (MessageTemplates.DoesNotExist, customer_details.DoesNotExist) as e:
        logger.error(f"Database error: {str(e)}")
        return JsonResponse({"status": "failed", "error": "Template or customer not found"}, status=404)
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return JsonResponse({"status": "failed", "error": "Invalid request data"}, status=400)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JsonResponse({"status": "failed", "error": "Internal server error"}, status=500)

# ============================================================
# 1️⃣1️⃣ CUSTOMER RECOMMENDATIONS API
# ============================================================
def customer_recommendations_api(request, customer_id):
    try:
        recommendations = get_user_based_recommendations(customer_id)
        return JsonResponse({
            "customer_id": customer_id,
            "recommendations": recommendations
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ============================================================
# 1️⃣2️⃣ GET ALL CUSTOMERS
# ============================================================
def get_all_customers(request):
    customers = customer_details.objects.all()
    data = [
        {"customer_id": c.id, "customer_name": c.fullname}
        for c in customers
    ]
    return JsonResponse({"customers": data})

# ============================================================
# 1️⃣3️⃣ GET CUSTOMER PHONE
# ============================================================
def customer_phone(request, cid):
    customer = customer_details.objects.filter(id=cid).first()
    if customer:
        return JsonResponse({"phone": customer.primarycontact})
    return JsonResponse({"phone": None})

# ============================================================
# 1️⃣4️⃣ MESSAGE LOG VIEW
# ============================================================
def message_log_view(request):
    try:
        logs = SentMessageLog.objects.all().order_by('-sent_at')[:100]
        return render(request, 'recommender/message_logs.html', {'logs': logs})
    except Exception as e:
        return render(request, 'recommender/message_logs.html', {'logs': [], 'error': str(e)})

# ============================================================
# SEND MESSAGE API (Final RapBooster Version)
# ============================================================
@csrf_exempt
def send_message_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body.decode())

        customer_name = data.get("customer_name")
        phone_number = data.get("phone_number")
        message = data.get("message")

        # Validation
        if not phone_number:
            return JsonResponse({"error": "Phone number missing"}, status=400)
        if not message:
            return JsonResponse({"error": "Message missing"}, status=400)

        # RapBooster API Key
        RAPBOOSTER_API_KEY = os.getenv("RAPBOOSTER_API_KEY") or "6538c8eff027d41e9151"
        RAPBOOSTER_URL = "https://api.rapbooster.com/v1/send"

        payload = {
            "apikey": RAPBOOSTER_API_KEY,
            "phone": phone_number,
            "message": message
        }

        # Call RapBooster
        response = requests.post(RAPBOOSTER_URL, json=payload, timeout=10)

        try:
            provider = response.json()
        except:
            provider = {"raw": response.text}

        success = (
            response.status_code == 200 and
            provider.get("status") == "success"
        )

        if success:
            return JsonResponse({
                "status": "success",
                "customer": customer_name,
                "phone": phone_number,
                "rapbooster_message_id": provider.get("message_id"),
                "queue_status": provider.get("queue_status"),
            })

        return JsonResponse({
            "status": "failed",
            "http_code": response.status_code,
            "provider_response": provider,
        }, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

from .rapbooster_api import send_whatsapp_message, send_email_message
from django.conf import settings
from django.core.mail import send_mail

from .models import SentMessageLog
from .rapbooster_api import send_recommendation_message

@csrf_exempt
def send_whatsapp(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=400)

    phone = request.POST.get("phone")
    message = request.POST.get("message")
    customer_name = request.POST.get("customer_name", "Unknown")

    from .rapbooster_api import send_recommendation_message

    status_code, response_text = send_recommendation_message(
        phone_number=phone,
        message=message,
        customer_name=customer_name
    )

    return JsonResponse({
        "status": status_code,
        "response": response_text
    })


@csrf_exempt
def send_email(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=400)

    # FIX — use request.POST instead of json.loads()
    email = request.POST.get("email")
    subject = request.POST.get("subject", "AI Recommendation")
    message = request.POST.get("message")
    customer_name = request.POST.get("customer_name", "Unknown")

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        SentMessageLog.objects.create(
            customer_name=customer_name,
            phone=email,
            message_text=message,
            status="Email Sent",
            api_response="SMTP OK"
        )

        return JsonResponse({"status": 200, "message": "Email sent"})

    except Exception as e:
        return JsonResponse({"status": 500, "error": str(e)})
