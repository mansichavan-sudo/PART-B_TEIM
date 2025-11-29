from django.urls import path
from . import views

app_name = 'schedule_meetings'  # Define app name for namespacing

urlpatterns = [
    path('schedule/', views.schedule_meeting, name='schedule_meeting'),
    path('meeting_list/', views.meeting_list, name='meeting_list'),
    path('display_meeting/', views.display_meeting, name='display_meeting'),
    # path('meetings/complete/<int:pk>/', views.complete_meeting, name='complete_meeting'),
]
