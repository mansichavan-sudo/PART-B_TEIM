# ai_calling/admin.py
from django.contrib import admin
from .models import VoiceTemplate, Campaign, CallLog

@admin.register(VoiceTemplate)
class VoiceTemplateAdmin(admin.ModelAdmin):
    list_display = ("template_name","language","created_at")
    search_fields = ("template_name",)

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("name","lead_type","service_type","schedule_type","active","last_run_at")
    list_filter = ("lead_type","service_type","schedule_type","active")

@admin.register(CallLog)
class CallLogAdmin(admin.ModelAdmin):
    list_display = ("phone","campaign","status","attempts","created_at")
    list_filter = ("status","campaign")
