from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import *
from .forms import CreateCharacterForm
from .models import Character

# Create your views here.


class CharacterCreation(FormView):
    template_name = "tierra_media/character-creation.html"
    form_class = CreateCharacterForm
    success_url = "/tierra-media/character-creation/success/"

    def check_name(self, form):
        name = form.cleaned_data.get("name")
        user = form.cleaned_data.get("user")
        if Character.objects.filter(name=name).filter(user=user).exists():
            # TODO: add error message / render error page
            return False
        return True

    def form_valid(self, form):
        if self.check_name(form):
            form.save()
            return super().form_valid(form)
        return super().form_invalid(form)


class CharacterCreationSuccess(TemplateView):
    template_name = "tierra_media/success.html"
