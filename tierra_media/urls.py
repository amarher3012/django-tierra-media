from django.contrib import admin
from django.urls import path
from tierra_media.views import PersonajesView, CharacterDetailsView
app_name = "tierra_media"

urlpatterns = [
    path("personajes/", PersonajesView.as_view(), name="characters"),
    path("personajes/<int:pk>", CharacterDetailsView.as_view(), name="character_details"),
]
