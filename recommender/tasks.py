from celery import shared_task
from recommender.utils import train_content_model, train_cf_svd
from recommender.models import PestRecommendation, SentMessageLog
from recommender.rapbooster_api import send_recommendation_message
from crmapp.models import customer_details as Customer


# ==========================================
# 🔹 Task 1: Re-train Recommenders
# ==========================================
@shared_task
def retrain_recommenders():
    """Retrain both recommender models (content & collaborative)."""
    train_content_model()
    train_cf_svd()
    return "✅ Recommenders retrained successfully"


# ==========================================
# 🔹 Task 2: Send Recommendations via API
# ==========================================
@shared_task
def send_recommendations_to_customers():
    """
    Loop through all stored PestRecommendations
    and send WhatsApp/SMS via RapBooster API.
    """
    sent_count = 0
    failed = 0

    for rec in PestRecommendation.objects.all():
        try:
            customer = Customer.objects.get(id=rec.customer_id)

            product_name = "Unknown Product"
            if hasattr(rec, "recommended_product_id"):
                product_name = str(rec.recommended_product_id)

            message = (
                f"Hi {customer.fullname}, "
                f"we recommend trying '{product_name}' for better results!"
            )

            # Send via RapBooster API
            status, response = send_recommendation_message(customer.primarycontact, message)
            print(f"✅ Sent to {customer.primarycontact}: {status}")

            # ✅ Correct log entry
            SentMessageLog.objects.create(
                customer_name=customer.fullname,
                phone=str(customer.primarycontact),
                message_text=message,
                status=str(status),
                api_response=str(response),
            )

            sent_count += 1

        except Exception as e:
            print(f"❌ Failed for Customer {rec.customer_id}: {e}")
            failed += 1

    return f"✅ Sent: {sent_count}, ❌ Failed: {failed}"
