import requests
from .models import SentMessageLog
from django.core.mail import send_mail
from django.conf import settings

API_URL = "https://rapbooster.ai/api/send"  # ✅ tested working endpoint
API_KEY = "6538c8eff027d41e9151"  # your RapBooster API key

 

# ==========================
#   RAPBOOSTER WHATSAPP API
# ==========================

def send_whatsapp_message(phone_number, message, customer_name="Unknown"):
    payload = {
        "phone": str(phone_number),
        "message": message
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        status = "Delivered" if response.status_code == 200 else "Failed"

        SentMessageLog.objects.create(
            customer_name=customer_name,
            phone=phone_number,
            message_text=message,
            status=status,
            api_response=response.text
        )

        return status, response.text

    except Exception as e:
        SentMessageLog.objects.create(
            customer_name=customer_name,
            phone=phone_number,
            message_text=message,
            status="Error",
            api_response=str(e)
        )
        return "Error", str(e)



# ==========================
#        EMAIL SENDER
# ==========================
def send_email_message(email, subject, message, customer_name="Unknown"):
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,   # FROM
            [email],                       # TO
            fail_silently=False,
        )

        SentMessageLog.objects.create(
            customer_name=customer_name,
            phone=email,
            message_text=message,
            status="Email Delivered",
            api_response="Email sent successfully."
        )

        return "Delivered", "Email Sent"

    except Exception as e:
        SentMessageLog.objects.create(
            customer_name=customer_name,
            phone=email,
            message_text=message,
            status="Email Error",
            api_response=str(e)
        )

        return "Error", str(e)


def send_recommendation_message(phone_number, message, customer_name="Unknown"):
    payload = {
        "phone": str(phone_number),
        "message": message
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=10)
        status = "Delivered" if response.status_code == 200 else "Failed"

        # Log to DB
        SentMessageLog.objects.create(
            customer_name=customer_name,
            phone=phone_number,
            message_text=message,
            status=status,
            api_response=response.text
        )

        return response.status_code, response.text

    except Exception as e:
        SentMessageLog.objects.create(
            customer_name=customer_name,
            phone=phone_number,
            message_text=message,
            status="Error",
            api_response=str(e)
        )
        return 500, str(e)
