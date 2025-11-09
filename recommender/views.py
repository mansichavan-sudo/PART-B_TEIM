from django.shortcuts import render
from django.db import connection
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json


from .models import MessageTemplate
from .recommender_engine import (
    get_content_based_recommendations,
    get_collaborative_recommendations,
    get_upsell_recommendations,
    get_crosssell_recommendations,
    generate_recommendations_for_user
)

# =====================================================
# 💻 UI Page: Interactive Recommendation System
# =====================================================
def recommendation_ui(request):
    """Display UI with message templates and tabs for recommendations"""
    templates = MessageTemplate.objects.all().order_by("template_type")
    return render(request, 'recommender/recommendations_ui.html', {'templates': templates})


# =====================================================
# 🧠 API: Content-Based Recommendations
# =====================================================
def recommendations_view(request):
    product_name = request.GET.get('product')
    if not product_name:
        return JsonResponse({'error': 'Please provide a product name.'}, status=400)

    results = get_content_based_recommendations(product_name)
    return JsonResponse({'recommended_products': results})


# =====================================================
# 🎯 API: Collaborative Recommendations
# =====================================================
def collaborative_view(request, customer_id):
    results = get_collaborative_recommendations(customer_id)
    return JsonResponse({'similar_customers': results})


# =====================================================
# 💹 API: Upsell Recommendations
# =====================================================
def upsell_view(request, product_id):
    results = get_upsell_recommendations(product_id)
    return JsonResponse({'upsell_suggestions': results})


# =====================================================
# 🔄 API: Cross-Sell Recommendations
# =====================================================
def crosssell_view(request, customer_id):
    results = get_crosssell_recommendations(customer_id)
    return JsonResponse({'cross_sell_suggestions': results})


# =====================================================
# 📊 Dashboard Page: All CRM-Based Recommendations
# =====================================================
def recommendation_dashboard(request):
    """Show all CRM recommendation data in a table."""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                c.name AS customer_name,
                bp.product_name AS base_product,
                rp.product_name AS recommended_product,
                pr.recommendation_type,
                pr.confidence_score
            FROM pest_recommendations pr
            JOIN customer_details c ON pr.customer_id = c.id
            JOIN product_details bp ON pr.base_product_id = bp.id
            JOIN product_details rp ON pr.recommended_product_id = rp.id
            ORDER BY pr.confidence_score DESC;
        """)
        rows = cursor.fetchall()

    data = [
        {
            "customer_name": row[0],
            "base_product": row[1],
            "recommended_product": row[2],
            "recommendation_type": row[3],
            "confidence_score": row[4],
        }
        for row in rows
    ]

    return render(request, "recommender/recommendation_dashboard.html", {"recommendations": data})


# =====================================================
# 🛍️ API: Fetch All Products
# =====================================================
def get_all_products(request):
    """Return list of all product names for dropdown."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT product_name FROM product_details ORDER BY product_name;")
        rows = cursor.fetchall()

    products = [row[0] for row in rows]
    return JsonResponse({'products': products})


# =====================================================
# 🤖 API: AI-Personalized Recommendations
# =====================================================
@csrf_exempt
@login_required
def api_ai_personalized(request):
    """
    Generate AI-powered personalized recommendations for a given customer.
    Endpoint: /api/ai-personalized/?customer_id=<id>
    """
    customer_id = request.GET.get('customer_id')

    if not customer_id:
        return JsonResponse({'error': 'Customer ID is required.'}, status=400)

    try:
        recommendations = generate_recommendations_for_user(
            user_id=int(customer_id),
            top_n=5
        )

        results = []
        for r in recommendations:
            results.append({
                "product_title": getattr(r, 'title', str(r)),
                "confidence_score": getattr(r, 'score', None)
            })

        return JsonResponse({
            'customer_id': customer_id,
            'recommendations': results
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



@csrf_exempt
def send_message_to_customer(request):
    if request.method == "POST":
        data = json.loads(request.body)
        customer_id = data.get("customer_id")
        message = data.get("message")

        if not customer_id or not message:
            return JsonResponse({"error": "Customer ID and message are required."}, status=400)

        # Example action — store in CRM logs or send via SMS API
        # send_sms(customer_id, message)  # Example integration
        print(f"📨 Message sent to Customer {customer_id}: {message}")

        return JsonResponse({"status": "success", "message": "Message sent successfully!"})

    return JsonResponse({"error": "Invalid request"}, status=400)



def generate_personalized_message(request, customer_id, product_id):
    """
    Generate personalized cross-sell/upsell message for a customer.
    """
    try:
        with connection.cursor() as cursor:
            # Get customer info
            cursor.execute("SELECT name FROM customer_details WHERE id = %s", [customer_id])
            customer = cursor.fetchone()
            if not customer:
                return JsonResponse({'error': 'Customer not found'}, status=404)
            customer_name = customer[0]

            # Get purchased product info
            cursor.execute("SELECT product_name FROM product_details WHERE id = %s", [product_id])
            product = cursor.fetchone()
            if not product:
                return JsonResponse({'error': 'Product not found'}, status=404)
            product_name = product[0]

            # Get recommendation
            cursor.execute("""
                SELECT p2.product_name, pr.recommendation_type
                FROM product_recommendations pr
                JOIN product_details p2 ON pr.recommended_product_id = p2.id
                WHERE pr.base_product_id = %s
            """, [product_id])
            rec = cursor.fetchone()

            if not rec:
                message = f"Hello {customer_name}, thank you for choosing {product_name}! 😊"
                return JsonResponse({'message': message})

            recommended_product, rec_type = rec

            message = (
                f"Hello {customer_name}, based on your last purchase of {product_name}, "
                f"we recommend our {recommended_product} ({rec_type}) for full protection! 🛡️"
            )

            return JsonResponse({
                'customer_name': customer_name,
                'base_product': product_name,
                'recommended_product': recommended_product,
                'recommendation_type': rec_type,
                'message': message
            })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_message_templates(request):
    """Return all message templates as JSON."""
    templates = MessageTemplate.objects.all().values("template_name", "template_type", "content")
    return JsonResponse(list(templates), safe=False)
