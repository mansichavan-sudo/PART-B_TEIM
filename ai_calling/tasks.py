# ai_calling/tasks.py
from celery import shared_task
from django.utils import timezone
from .models import Campaign, CallLog, VoiceTemplate
from .services.provider import make_call
from django.conf import settings
import requests
import time
import logging

logger = logging.getLogger(__name__)

def fill_template(script: str, lead: dict):
    # Replace placeholders like [Name] with lead keys (case-insensitive)
    text = script
    for k, v in (lead or {}).items():
        placeholder = f'[{k}]'
        text = text.replace(placeholder, str(v))
    return text

@shared_task(bind=True)
def send_campaign_calls(self, campaign_id, leads=None):
    """
    campaign_id: id of Campaign
    leads: optional list of dicts: [{ "phone": "+91...", "Name": "Prachi", "Product": "X" }, ...]
    If leads is None and CRM_LEADS_ENDPOINT set, it will attempt to fetch leads from CRM.
    """
    try:
        campaign = Campaign.objects.get(pk=campaign_id)
    except Campaign.DoesNotExist:
        logger.error("Campaign not found %s", campaign_id)
        return {"error": "campaign not found"}

    # get template script
    template = campaign.template
    if not template:
        logger.error("Campaign %s has no template", campaign_id)
        return {"error": "no template"}

    # fetch leads if not provided
    if not leads:
        crm_url = getattr(settings, "CRM_LEADS_ENDPOINT", "")
        if crm_url:
            try:
                resp = requests.get(crm_url, headers={"Authorization": f"Bearer {getattr(settings,'CRM_API_TOKEN','')}"}, params={"lead_type": campaign.lead_type, "service_type": campaign.service_type})
                resp.raise_for_status()
                leads = resp.json()  # expecting a list of dicts with "phone" and other fields
            except Exception as e:
                logger.exception("Failed to fetch leads from CRM")
                return {"error": "crm fetch failed", "detail": str(e)}
        else:
            # No leads available - you can change this to raise or use a test list
            logger.warning("No leads passed and no CRM configured. Nothing to do.")
            return {"error": "no leads"}

    results = []
    for lead in leads:
        phone = lead.get("phone") if isinstance(lead, dict) else lead
        if not phone:
            continue
        # create call log
        log = CallLog.objects.create(campaign=campaign, phone=phone, status="pending", attempts=0)
        attempt = 0
        success = False
        last_error = None
        while attempt <= campaign.retry_attempts and not success:
            attempt += 1
            log.attempts = attempt
            log.started_at = timezone.now()
            log.status = "initiated"
            log.save(update_fields=["attempts", "started_at", "status"])
            try:
                text_to_say = fill_template(template.voice_script, lead if isinstance(lead, dict) else {})
                twilio_sid = make_call(
                to_number=phone,
                variable_values=lead if isinstance(lead, dict) else {}  # lead dict with placeholders
                                      )

                log.twilio_sid = twilio_sid
                log.status = "success"
                log.finished_at = timezone.now()
                log.save()
                success = True
            except Exception as e:
                last_error = str(e)
                logger.exception("Call to %s failed (attempt %s)", phone, attempt)
                log.status = "failed"
                log.error_text = last_error
                log.finished_at = timezone.now()
                log.save()
                # optional small backoff
                time.sleep(1)
        results.append({"phone": phone, "success": success, "error": last_error})

    # update campaign last_run_at
    campaign.last_run_at = timezone.now()
    campaign.save(update_fields=["last_run_at"])
    return {"campaign": campaign_id, "results": results}

# periodic check: run the scheduled campaigns if due
@shared_task
def check_and_run_scheduled_campaigns():
    now = timezone.now()
    # scheduled (one-time): schedule_datetime <= now and last_run_at is null (or older)
    scheduled = Campaign.objects.filter(active=True, schedule_type="scheduled", schedule_datetime__lte=now)
    for c in scheduled:
        send_campaign_calls.delay(c.id)

    # recurring: if recurrence_interval_minutes provided and (last_run_at is None or now >= last_run_at + interval)
    recurring = Campaign.objects.filter(active=True, schedule_type="recurring").exclude(recurrence_interval_minutes__isnull=True)
    for c in recurring:
        if not c.last_run_at:
            send_campaign_calls.delay(c.id)
        else:
            next_time = c.last_run_at + timezone.timedelta(minutes=c.recurrence_interval_minutes)
            if now >= next_time:
                send_campaign_calls.delay(c.id)

