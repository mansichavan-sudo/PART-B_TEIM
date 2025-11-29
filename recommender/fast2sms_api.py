import requests
from django.conf import settings
from recommender.models import SentMessageLog

FAST2SMS_API_KEY = getattr(settings, "lmECgGI0f57i2x94H81uqVtTyObKhzFZMNLXA3oapseB6RQcJD5ZsIrukQRLzoCcKHWaBF6TliSXdUgA")
FAST2SMS_URL = "https://www.fast2sms.com/dev/bulkV2"

def send_recommendation_message(phone_number, message, customer_name="Unknown"):
    """
    Send SMS using Fast2SMS API and log the result in the database.
    """
    payload = {
        "sender_id": "TXTIND",
        "message": message,
        "language": "english",
        "route": "v3",
        "numbers": str(phone_number),
    }

    headers = {
        "authorization": FAST2SMS_API_KEY,
        "cache-control": "no-cache",
        "accept": "application/json",
    }

    try:
        # ✅ Use POST
        response = requests.post(FAST2SMS_URL, data=payload, headers=headers, timeout=10)
        status = "Delivered" if response.status_code == 200 else "Failed"

        SentMessageLog.objects.create(
            customer_name=customer_name,
            phone=phone_number,
            message_text=message,
            status=status,
            api_response=response.text,
        )

        print(f"✅ SMS sent to {phone_number} | Status: {status}")
        return response.status_code, response.text

    except Exception as e:
        SentMessageLog.objects.create(
            customer_name=customer_name,
            phone=phone_number,
            message_text=message,
            status="Error",
            api_response=str(e),
        )
        print(f"❌ Error sending SMS: {e}")
        return 500, str(e)
