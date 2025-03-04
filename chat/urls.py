from django.urls import path
from chat.views import chat
urlpatterns = [
    path('chat/', chat, name='chat'),
]