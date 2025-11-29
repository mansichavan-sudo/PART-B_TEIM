# email_senders/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('automate_lead_emails/', views.automate_lead_emails, name='automate_lead_emails'),
]