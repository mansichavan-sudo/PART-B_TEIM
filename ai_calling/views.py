# ai_calling/views.py

# --- Django / DRF imports ---
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from django.shortcuts import render, get_object_or_404
from django.utils import timezone

# --- Local imports ---
from .models import VoiceTemplate, Campaign, CallLog
from .serializers import VoiceTemplateSerializer, CampaignSerializer, CallLogSerializer
from .tasks import send_campaign_calls
from .services.provider import make_call


# ---------------------------
#  API / Backend Views
# ---------------------------

class VoiceTemplateViewSet(viewsets.ModelViewSet):
    queryset = VoiceTemplate.objects.all().order_by("-created_at")
    serializer_class = VoiceTemplateSerializer

class CampaignViewSet(viewsets.ModelViewSet):
    queryset = Campaign.objects.all().order_by("-created_at")
    serializer_class = CampaignSerializer

    @action(detail=True, methods=["post"])
    def run(self, request, pk=None):
        campaign = self.get_object()
        leads = request.data.get("leads")
        send_campaign_calls.delay(campaign.id, leads)
        return Response({"status": "queued"}, status=status.HTTP_202_ACCEPTED)

class TestCallView(APIView):
    def post(self, request, *args, **kwargs):
        phone = request.data.get("phone")
        template_id = request.data.get("template_id")
        placeholders = request.data.get("placeholders", {})

        if not phone or not template_id:
            return Response({"error":"phone & template_id required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            template = VoiceTemplate.objects.get(pk=template_id)
        except VoiceTemplate.DoesNotExist:
            return Response({"error":"template not found"}, status=status.HTTP_404_NOT_FOUND)

        text = template.voice_script
        for k, v in (placeholders or {}).items():
            text = text.replace(f'[{k}]', str(v))
        try:
            sid = make_call(
                to_number=phone,
             #   say_text=text,
             #   from_number=None,
              #  voice=template.tts_voice,
              #  language=template.language,
                variable_values=placeholders
            )
            return Response({"status":"initiated", "twilio_sid": sid})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

# ---------------------------
#  Frontend Views
# ---------------------------

# Campaign Views
def campaign_list(request):
    campaigns = Campaign.objects.all().order_by("-created_at")
    return render(request, "ai_calling/campaign_list.html", {"campaigns": campaigns})

def campaign_create(request):
    # Use the existing campaign_form.html for both create/edit
    return render(request, "ai_calling/campaign_form.html", {"campaign": None})

def campaign_edit(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    return render(request, "ai_calling/campaign_form.html", {"campaign": campaign})

# Template Views
def template_list(request):
    templates = VoiceTemplate.objects.all().order_by("-created_at")
    return render(request, "ai_calling/template_list.html", {"templates": templates})

def template_create(request):
    # Use the existing template_form.html for both create/edit
    return render(request, "ai_calling/template_form.html", {"template": None})
