import copy
from django.views.generic import *
from .forms import CreateCharacterForm
from .models import Character, NPC
from .constants import NPCS


class NPC_preparations:
    # TODO: create migration with fixed data (factions, locations and races)
    # TODO: faction, location and race need to be an instance of said objects
    def create_npcs():
        npcs = copy.deepcopy(NPCS)
        for npc in npcs:
            npc.update({"character": Character.objects.get(pk=1)})
            npc_created = NPC(**npc)
            npc_created.save()


class CharacterCreation(CreateView):
    template_name = "character-creation/character-creation.html"
    form_class = CreateCharacterForm
    success_url = "/tierra-media/character-creation/success/"
    npc = NPC_preparations()

    def check_name(self, form):
        name = form.cleaned_data.get("name")
        # TODO: replace user with session user
        user = form.cleaned_data.get("user")
        if Character.objects.filter(name=name).filter(user=user).exists():
            form.add_error("name", "Ya tienes un personaje con ese nombre.")
            return False
        return True

    def form_valid(self, form):
        if self.check_name(form):
            self.npc.create_npcs()
            return super().form_valid(form)
        return super().form_invalid(form)


class CharacterCreationSuccess(TemplateView):
    template_name = "character-creation/success.html"


class Weapons(UpdateView):
    pass


class Armors(UpdateView):
    pass
