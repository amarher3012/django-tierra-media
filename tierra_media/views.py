from django.shortcuts import render
from .models import *
from django.views.generic import ListView

class PersonajesView(ListView):
    model = Character
    template_name = "tierra_media/personajes.html"
    context_object_name = "characters"

    def get_queryset(self):
        return Character.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['characters'] = self.get_queryset()
        return context
