from django.urls import path
from . import views

urlpatterns = [
    path("chat/", views.chat, name="chat"),  # Make sure the path reflects the chat view
    path("ask_question/", views.ask_question, name="ask_question"),
]