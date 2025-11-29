from django.urls import path
from .views import generate_invoice_pdf

urlpatterns = [
    # Other URL patterns
    path('invoice/pdf/<int:invoice_id>/', generate_invoice_pdf, name='generate_invoice_pdf'),
    path('invoice/pdf/<int:invoice_id>/<str:action>/', generate_invoice_pdf, name='generate_invoice_pdf_action'),
]