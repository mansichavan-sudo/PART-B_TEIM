# ai_calling/services/twilio_service.py
import os, logging
from twilio.rest import Client

logger = logging.getLogger(__name__)

def get_twilio_client():
    sid = os.environ.get("TWILIO_ACCOUNT_SID")
    token = os.environ.get("TWILIO_AUTH_TOKEN")
    if not sid or not token:
        raise RuntimeError("TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN not configured")
    return Client(sid, token)

def make_call(to_number: str, say_text: str, from_number: str = None, voice: str = None, language: str = "en-IN"):
    """
    Place a call using Twilio and return the call SID.
    This uses simple TwiML with <Say>. For production you might host a TwiML URL instead.
    """
    client = get_twilio_client()
    from_number = from_number or os.environ.get("TWILIO_DEFAULT_CALLER")
    if not from_number:
        raise RuntimeError("No caller ID configured (TWILIO_DEFAULT_CALLER or campaign.caller_id)")

    say_attrs = ''
    if voice:
        say_attrs += f' voice="{voice}"'
    if language:
        say_attrs += f' language="{language}"'

    twiml = f'<Response><Say{say_attrs}>{say_text}</Say></Response>'
    try:
        call = client.calls.create(to=to_number, from_=from_number, twiml=twiml)
        logger.info("Placed call %s -> %s (sid=%s)", from_number, to_number, call.sid)
        return call.sid
    except Exception as e:
        logger.exception("Twilio call failed")
        raise
