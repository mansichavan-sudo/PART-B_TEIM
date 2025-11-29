# ai_calling/services/provider.py
from django.conf import settings

if getattr(settings, "USE_VAPI", False):
    from .vapi_service import make_call
else:
    from .twilio_service import make_call
