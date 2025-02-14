from django.contrib import admin
from django.urls import path, include
from .views import *

app_name = "tierra_media"
urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("cuentas/", include("django.contrib.auth.urls")),
    path("cuentas/registro", RegisterView.as_view(), name="register"),
    path("cuentas/activar", ActivateAccount.as_view(), name="activate"),
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
