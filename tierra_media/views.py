from django.shortcuts import render
from django.views.generic import *
from .forms import CreateCharacterForm

# Create your views here.


class CharacterCreation(FormView):
    template_name = "character-creation.html"
    form_class = CreateCharacterForm
    success_url = "/tierra-media/success/"
