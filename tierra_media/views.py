from django.views.generic import *
from .forms import CreateCharacterForm
from .models import Character


class CharacterCreation(CreateView):
    template_name = "character-creation.html"
    form_class = CreateCharacterForm
    success_url = "/tierra-media/character-creation/success/"

    def check_name(self, form):
        name = form.cleaned_data.get("name")
        user = form.cleaned_data.get("user")
        if Character.objects.filter(name=name).filter(user=user).exists():
            form.add_error("name", "Ya tienes un personaje con ese nombre.")
            return False
        return True

    def form_valid(self, form):
        if self.check_name(form):
            return super().form_valid(form)
        return super().form_invalid(form)


class CharacterCreationSuccess(TemplateView):
    template_name = "success.html"
