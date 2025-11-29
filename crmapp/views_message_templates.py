from django.http import JsonResponse
from crmapp.models import MessageTemplates, customer_details, Product
from recommender.models import PestRecommendation

def get_template_content(request, template_id, customer_id):
    try:
        template = MessageTemplates.objects.get(id=template_id)
        customer = customer_details.objects.get(id=customer_id)

        # Find recommended product for this customer (from your recommendation engine)
        rec = PestRecommendation.objects.filter(customer_id=customer_id).first()

        recommended_product = rec.recommended_product.name if rec else ""
        base_product = rec.base_product.name if rec else ""

        # Prepare placeholder values
        data = {
            "subject": template.subject or "",
            "body": template.body,
            "customer_name": customer.customer_name,
            "product": base_product,
            "recommended_product": recommended_product,
        }

        return JsonResponse({"status": "success", "data": data})

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})
