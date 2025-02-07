from .views import *
from django.contrib import admin
from django.urls import path

app_name = "tierra_media"
urlpatterns = [
    path(
        "character-creation/",
        CharacterCreation.as_view(),
        name="character_creation",
    ),
]
