from django.urls import path
from .views import scan_visiting_card

urlpatterns = [
    path('scan/', scan_visiting_card, name='scan_visiting_card'),
]       
    