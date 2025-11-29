# ai_calling/services/vapi_service.py
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

VAPI_BASE = getattr(settings, "VAPI_API_URL", "https://api.vapi.ai")
VAPI_KEY = getattr(settings, "VAPI_API_KEY", None)
DEFAULT_ASSISTANT = getattr(settings, "VAPI_ASSISTANT_ID", None)
DEFAULT_PHONE_ID = getattr(settings, "VAPI_PHONE_NUMBER_ID", None)


def _headers():
    if not VAPI_KEY:
        raise RuntimeError("VAPI_API_KEY not set in settings")
    return {
        "Authorization": f"Bearer {VAPI_KEY}",
        "Content-Type": "application/json",
    }


def make_call(
    to_number: str,
    assistant_id: str = None,
    phone_number_id: str = None,
    variable_values: dict = None,
    max_duration_seconds: int = 600,
    recording_enabled: bool = True,
):
    """
    Initiates an outbound call via Vapi REST API.
    Returns call_id (string) if successful.
    """

    if not to_number:
        raise ValueError("to_number is required")

    assistant_id = assistant_id or DEFAULT_ASSISTANT
    phone_number_id = phone_number_id or DEFAULT_PHONE_ID

    if not assistant_id:
        raise RuntimeError("VAPI_ASSISTANT_ID is required in settings or pass as parameter")

    payload = {
        "customer": {
            "number": to_number,   # ✅ use the actual number
            "numberE164CheckEnabled": False,
        },
        "assistantId": assistant_id,
        "variableValues": variable_values or {},
        "maxDurationSeconds": max_duration_seconds,
        "artifactPlan": {"recordingEnabled": bool(recording_enabled)},
    }

    if phone_number_id:
        payload["phoneNumberId"] = phone_number_id

    url = f"{VAPI_BASE}/call"
    logger.info("Sending call request to Vapi: %s", payload)

    resp = requests.post(url, headers=_headers(), json=payload, timeout=30)

    if resp.status_code >= 400:
        logger.error("Vapi call failed: %s %s", resp.status_code, resp.text)
        raise Exception(f"Vapi call failed: {resp.status_code} {resp.text}")

    data = resp.json()
    call_id = data.get("id") or (data.get("calls") and data["calls"][0].get("id"))
    logger.info("Vapi call initiated. ID=%s", call_id)
    return call_id or data
