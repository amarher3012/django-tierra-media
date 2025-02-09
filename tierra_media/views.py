from django.shortcuts import render
from .models import *
from django.views.generic import ListView, DetailView

class PersonajesView(ListView):
    model = Character
    template_name = "tierra_media/characters.html"
    context_object_name = "characters"

    def get_queryset(self):
        return Character.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['characters'] = self.get_queryset()
        return context

class CharacterDetailsView(DetailView):
    model = Character
    template_name = "tierra_media/character_details.html"
    context_object_name = "character"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['character'] = Character.objects.get(pk=self.kwargs['pk'])
        return context