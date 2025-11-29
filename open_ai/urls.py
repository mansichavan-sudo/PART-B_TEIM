from django.urls import path
from . import views

urlpatterns = [
    path('chatbot/', views.chatbotview, name='chatbotview'),
    path('chatbot/clear/', views.clear_conversation, name='clear_conversation'), 
]
