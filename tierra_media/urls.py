from django.contrib import admin
from django.urls import path, include

from . import views

app_name = "tierra_media"
urlpatterns = [
    path("", views.index, name="index"),
    path("cuentas/", include("django.contrib.auth.urls")),
]
