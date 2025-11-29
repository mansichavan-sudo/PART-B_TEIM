# ai_calling/serializers.py
from rest_framework import serializers
from .models import VoiceTemplate, Campaign, CallLog

class VoiceTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoiceTemplate
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

class CampaignSerializer(serializers.ModelSerializer):
    template = VoiceTemplateSerializer(read_only=True)
    template_id = serializers.PrimaryKeyRelatedField(source="template", queryset=VoiceTemplate.objects.all(), write_only=True, required=False, allow_null=True)

    class Meta:
        model = Campaign
        fields = [
            "id","name","description","lead_type","service_type","language","caller_id",
            "template","template_id","retry_attempts","schedule_type","schedule_datetime","recurrence_interval_minutes",
            "recommendation_enabled","upsell_text","crosssell_text","fallback_whatsapp","fallback_email","fallback_voicemail",
            "active","last_run_at","created_at","updated_at",
        ]
        read_only_fields = ("id","last_run_at","created_at","updated_at")

class CallLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallLog
        fields = "__all__"
