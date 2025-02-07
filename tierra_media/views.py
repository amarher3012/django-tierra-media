from django.shortcuts import render
from django.views.generic import *
from .forms import CreateCharacterForm
from .models import Character

# Create your views here.


class CharacterCreation(FormView):
    template_name = "character-creation.html"
    form_class = CreateCharacterForm
    success_url = "/tierra-media/character-creation/success/"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class CharacterCreationSuccess(TemplateView):
    template_name = "success.html"
    # TODO: Add wait + redirect back to the menu
