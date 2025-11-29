# dashboard/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('view/', views.dashboard_view, name='dashboard'),
    # path('index/', views.calendar_view, name='calendar_view'),
    path('meeting-data/', views.meeting_data, name='meeting-data'),  # API endpoint for event data
    # path('user_login', views.dashboard_view, name='user_login'),  # New path for the dashboard view
]
