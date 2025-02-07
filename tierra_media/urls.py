from .views import *
from django.urls import path

app_name = "tierra_media"
urlpatterns = [
    path(
        "character-creation/",
        CharacterCreation.as_view(),
        name="character_creation",
    ),
    path(
        "character-creation/success/",
        CharacterCreationSuccess.as_view(),
        name="success",
    ),
]
