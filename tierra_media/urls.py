from django.contrib import admin
from django.urls import path, include
from .views import *

app_name = "tierra_media"
urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/signin", RegisterView.as_view(), name="register"),
    path("accounts/activate", ActivateAccount.as_view(), name="activate"),
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
    path("characters/", CharactersView.as_view(), name="characters"),
    path(
        "characters/<int:pk>", CharacterDetailsView.as_view(), name="character_details"
    ),
    path(
        "characters/<int:pk>/equip-weapon", EquipWeapon.as_view(), name="equip_weapon"
    ),
    path("characters/<int:pk>/get-weapons", GetWeapons.as_view(), name="get_weapons"),
    path(
        "characters/<int:pk>/relationships",
        RelationShips.as_view(),
        name="relationships",
    ),
    path("characters/<int:pk>/shop", Shop.as_view(), name="shop"),
    path("characters/<int:pk>/move/", Move.as_view(), name="move"),
    path(
        "characters/<int:pk>/move/success/", MoveSuccess.as_view(), name="move_success"
    ),
]
