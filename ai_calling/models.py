from django.db import models

class VoiceTemplate(models.Model):
    LANG_CHOICES = (
        ("en", "English"),
        ("hi", "Hindi"),
        ("mr", "Marathi"),
    )

    template_name = models.CharField(max_length=200)
    language = models.CharField(max_length=8, choices=LANG_CHOICES, default="en")
    tts_voice = models.CharField(
        max_length=128, blank=True, null=True,
        help_text="Optional TTS voice identifier supported by Twilio (e.g., 'alice')."
    )
    voice_script = models.TextField(
        help_text="Script content. Use placeholders like [Name], [Product]."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.template_name


class Campaign(models.Model):
    LEAD_TYPE = (
        ("hot", "Hot"),
        ("warm", "Warm"),
        ("cold", "Cold"),
        ("close_win", "Close Win"),
        ("close_loss", "Close Loss"),
        ("not_interested", "Not Interested"),
    )

    SERVICE_TYPE = (
        ("service", "Service"),
        ("product", "Product"),
    )

    SCHEDULE_TYPE = (
        ("immediate", "Immediate"),
        ("scheduled", "Scheduled"),
        ("recurring", "Recurring"),
    )

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    lead_type = models.CharField(max_length=32, choices=LEAD_TYPE)
    service_type = models.CharField(max_length=16, choices=SERVICE_TYPE, default="service")
    language = models.CharField(max_length=8, choices=VoiceTemplate.LANG_CHOICES, default="en")
    caller_id = models.CharField(
        max_length=32, blank=True, null=True,
        help_text="Twilio number (E.164 format) or leave blank to use default."
    )

    template = models.ForeignKey(
        VoiceTemplate, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="campaigns"
    )
    retry_attempts = models.PositiveSmallIntegerField(default=2)

    schedule_type = models.CharField(max_length=16, choices=SCHEDULE_TYPE, default="immediate")
    schedule_datetime = models.DateTimeField(blank=True, null=True)
    recurrence_interval_minutes = models.PositiveIntegerField(
        blank=True, null=True,
        help_text="If recurring: interval in minutes (e.g., 1440 for daily)."
    )

    recommendation_enabled = models.BooleanField(default=False)
    upsell_text = models.TextField(blank=True)
    crosssell_text = models.TextField(blank=True)

    fallback_whatsapp = models.BooleanField(default=False)
    fallback_email = models.BooleanField(default=False)
    fallback_voicemail = models.BooleanField(default=False)

    active = models.BooleanField(default=True)
    last_run_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class CallLog(models.Model):
    STATUS = (
        ("pending", "Pending"),
        ("initiated", "Initiated"),
        ("success", "Success"),
        ("failed", "Failed"),
        ("no_answer", "No Answer"),
    )

    campaign = models.ForeignKey(
        "Campaign",
        null=True, blank=True,
        on_delete=models.SET_NULL, related_name="call_logs"
    )
    phone = models.CharField(max_length=48)
    status = models.CharField(max_length=16, choices=STATUS, default="pending")
    attempts = models.PositiveSmallIntegerField(default=0)
    twilio_sid = models.CharField(max_length=128, blank=True, null=True)
    error_text = models.TextField(blank=True)

    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.phone} [{self.status}]"
