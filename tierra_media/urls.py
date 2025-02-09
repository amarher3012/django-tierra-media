from django.contrib import admin
from django.urls import path
from tierra_media.views import PersonajesView
app_name = "tierra_media"

urlpatterns = [
    path("personajes/", PersonajesView.as_view()),
]
