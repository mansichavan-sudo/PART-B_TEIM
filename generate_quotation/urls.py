from django.urls import path
from .views import generate_quotation_pdf

urlpatterns = [
    # Other URL patterns
    path('quotation/pdf/<int:quotation_id>/', generate_quotation_pdf, name='generate_quotation_pdf'),
    path('quotation/pdf/<int:quotation_id>/<str:action>/', generate_quotation_pdf, name='generate_quotation_pdf_action'),
]