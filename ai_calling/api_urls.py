# ai_calling/api_urls.py
from rest_framework import routers
from .views import VoiceTemplateViewSet, CampaignViewSet, TestCallView
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r"templates", VoiceTemplateViewSet, basename="template")
router.register(r"campaigns", CampaignViewSet, basename="campaign")

urlpatterns = [
    path("", include(router.urls)),
    path("test-call/", TestCallView.as_view(), name="test-call"),
]
