from django.contrib import admin
from django.urls import path, include
from .views import *

app_name = "tierra_media"
urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("cuentas/", include("django.contrib.auth.urls")),
    path("cuentas/registro", RegisterView.as_view(), name="register"),
    path("cuentas/activar", ActivateAccount.as_view(), name="activate"),
    path("characters/", CharactersView.as_view(), name="characters"),
    path("characters/<int:pk>", CharacterDetailsView.as_view(), name="character_details"),
    path("characters/<int:pk>/equip-weapon", EquipWeapon.as_view(), name="equip_weapon"),
    path("characters/<int:pk>/move-character", MoveCharacter.as_view(), name="move_character"),
    path("characters/<int:pk>/shop", Shop.as_view(), name="shop"),
]
