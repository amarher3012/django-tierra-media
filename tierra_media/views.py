from gc import get_objects

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.core.files import File
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlencode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django.views import View
from django.views.generic import *

from .forms import CustomUserCreationForm, CreateCharacterForm
from .models import Character, Weapon, Armor, Location, Faction, Race, Backpack
from .constants import npc_init, weapons_init, armors_init


class RegisterView(FormView):
    template_name = "registration/signin.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("tierra_media:index")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = True
        user.save()

        token = default_token_generator.make_token(user)

        uid = user.pk

        token_url = self.build_activation_url(uid, token)

        #self.send_activation_email(user, token_url)

        messages.success(
            self.request,
            f"Cuenta {user.username} creada exitosamente. En breves te llegará un correo de verificación.",
        )

        return super().form_valid(form)

    def build_activation_url(self, uid, token):
        return f"{get_current_site(self.request).domain}{reverse_lazy('tierra_media:activate')}?{urlencode({'uid': uid, 'token': token})}"

    def send_activation_email(self, user, token_url):
        subject = "Verificación de correo electrónico"
        message = (
            f"Hola {user.username},\n\nPara activar tu cuenta, haz clic en el siguiente enlace:\n\n{token_url}\n\n"
            f"Si no solicitaste esta cuenta, puedes ignorar este correo."
        )
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user.email]

        send_mail(subject, message, from_email, recipient_list)


class ActivateAccount(View):
    def get(self, request):
        uid = request.GET.get("uid")
        token = request.GET.get("token")

        if not uid or not token:
            messages.error(request, "Token inválido o expirado.")
            return redirect("tierra_media:register")

        try:
            user = get_user_model().objects.get(pk=uid)
        except get_user_model().DoesNotExist:
            messages.error(request, "El usuario no existe.")
            return redirect("tierra_media:register")

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            messages.success(
                request,
                "Tu cuenta ha sido activada con éxito. Ahora puedes iniciar sesión.",
            )
            # Tras activar al usuario, los NPCs se crean y asignan a ese usuario
            NPC_preparations.create_npcs(user)
            WeaponPreparations.create_weapons(user)
            ArmorPreparations.create_armors(user)

            return redirect("tierra_media:login")
        else:
            messages.error(
                request, "El enlace de activación no es válido o ha expirado."
            )
            return redirect("tierra_media:register")


class IndexView(ListView):
    model = Character
    template_name = "tierra_media/index.html"
    context_object_name = "characters"

    def get_queryset(self):
        user = self.request.user.pk
        characters = Character.objects.filter(user=user)
        return characters

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["characters"] = self.get_queryset()
        return context


class CharacterCreation(LoginRequiredMixin, CreateView):
    template_name = "character-creation/character-creation.html"
    form_class = CreateCharacterForm
    success_url = '/tierra-media/character-creation/add-backpack'

    def check_name(self, form):
        name = form.cleaned_data.get("name")
        user = self.request.user

        if Character.objects.filter(name=name, user=user).exists():
            form.add_error("name", "Ya tienes un personaje con ese nombre.")
            return False
        return True

    def add_icon(self, form):
        sex = form.cleaned_data.get("sex")
        race = form.cleaned_data.get("race")
        if sex == "M":
            male_icon = open(
                f"static/icons/character-icons/male/{race.name.lower()}.png",
                "rb",
            )

            obj = form.save(commit=False)
            obj.icon = File(male_icon)
        elif sex == "F":
            female_icon = open(
                f"static/icons/character-icons/female/{race.name.lower()}.png",
                "rb",
            )

            obj = form.save(commit=False)
            obj.icon = File(female_icon)

    def form_valid(self, form):
        if self.check_name(form):
            self.add_icon(form)
            form.instance.user = self.request.user
            messages.success(self.request, "Personaje creado con éxito.")
            return super().form_valid(form)

        messages.error(self.request, "Ocurrió un error al intentar crear el personaje.")
        return super().form_invalid(form)


class AddBackpack(View):
    def get(self, request):
        character = Character.objects.all().last()
        Backpack.objects.create(owner=character)
        messages.success(request, "Backpack creada con exito.")
        return redirect(reverse_lazy("tierra_media:character_details", kwargs={"pk": character.id}))


class CharacterCreationSuccess(TemplateView):
    template_name = "character-creation/success.html"


class NPC_preparations:
    def create_npcs(user):
        npcs = npc_init()
        for npc in npcs:
            npc_name = npc.get("name")
            faction_name = npc.pop("faction")
            location_name = npc.pop("location")
            race_name = npc.pop("race")

            faction = Faction.objects.get(name__iexact=faction_name)
            location = Location.objects.get(name__iexact=location_name)
            race = Race.objects.get(name__iexact=race_name)

            try:
                with open(
                    f"static/icons/character-icons/npcs/{npc_name.lower()}.png",
                    "rb",
                ) as npc_icon:
                    npc.update(
                        {
                            "icon": File(npc_icon),
                            "user": user,
                            "faction": faction,
                            "location": location,
                            "race": race,
                        }
                    )
                    npc_object = Character(**npc)
                    npc_object.save()
            except FileNotFoundError:
                npc.update(
                    {
                        "user": user,
                        "faction": faction,
                        "location": location,
                        "race": race,
                    }
                )
                npc_object = Character(**npc)
                npc_object.save()


class CharactersView(LoginRequiredMixin, ListView):
    model = Character
    template_name = "tierra_media/characters.html"
    context_object_name = "characters"

    def get_queryset(self):
        key_user = self.request.user.pk
        characters = Character.objects.filter(user=key_user)
        return characters

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["characters"] = self.get_queryset()
        return context


class CharacterDetailsView(LoginRequiredMixin, DetailView):
    model = Character
    template_name = "tierra_media/character_menu.html"
    context_object_name = "character"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        character = self.get_object()
        # context["character"] = model_to_dict(character, exclude=["user"])
        context["character"] = Character.objects.get(pk=character.pk)

        user = self.request.user
        user_characters = Character.objects.filter(user=user)

        faction = character.faction.name
        relationships = {"allies": [], "enemies": [], "neutrals": []}

        others = user_characters.exclude(pk=character.pk)

        for other in others:
            other_faction = other.faction.name

            match faction:
                case "La Comunidad del Anillo":
                    match other_faction:
                        case "La Comunidad del Anillo" | "Rivendel":
                            relationships["allies"].append(other)
                        case "Isengard" | "Mordor":
                            relationships["enemies"].append(other)
                        case _:
                            relationships["neutrals"].append(other)

                case "Isengard" | "Mordor":
                    match other_faction:
                        case "Isengard" | "Mordor":
                            relationships["allies"].append(other)
                        case _:
                            relationships["enemies"].append(other)

                case "Rivendel":
                    match other_faction:
                        case "Rivendel" | "La Comunidad del Anillo":
                            relationships["allies"].append(other)
                        case "Isengard" | "Mordor":
                            relationships["enemies"].append(other)
                        case _:
                            relationships["neutrals"].append(other)

                case "Lothlorien":
                    match other_faction:
                        case "Lothlorien":
                            relationships["allies"].append(other)
                        case "Isengard" | "Mordor":
                            relationships["enemies"].append(other)
                        case _:
                            relationships["neutrals"].append(other)

        context["relationships"] = relationships
        return context


class WeaponPreparations:
    def create_weapons(user):
        weapons = weapons_init()
        for weapon in weapons:
            weapon_type = weapon.get("type")
            try:
                with open(
                    f"static/icons/weapon-icons/{weapon_type.lower()}.png",
                    "rb",
                ) as weapon_icon:
                    weapon.update(
                        {
                            "icon": File(weapon_icon),
                            "user": user,
                        }
                    )
                    weapon_object = Weapon(**weapon)
                    weapon_object.save()
            except FileNotFoundError:
                weapon.update(
                    {
                        "user": user,
                    }
                )
                weapon_object = Weapon(**weapon)
                weapon_object.save()


class ArmorPreparations:
    def create_armors(user):
        armors = armors_init()
        for armor in armors:
            armor_name = armor.get("name")
            try:
                with open(
                    f"static/icons/armor-icons/{armor_name.lower()}.png",
                    "rb",
                ) as armor_icon:
                    armor.update(
                        {
                            "icon": File(armor_icon),
                            "user": user,
                        }
                    )
                    armor_object = Armor(**armor)
                    armor_object.save()
            except FileNotFoundError:
                armor.update(
                    {
                        "user": user,
                    }
                )
                armor_object = Armor(**armor)
                armor_object.save()


class GetWeapons(LoginRequiredMixin, ListView):
    model = Weapon
    template_name = "tierra_media/get_weapons.html"
    context_object_name = "weapons"

    def get_queryset(self):
        user = self.request.user.pk
        weapons = Weapon.objects.filter(user=user, backpack=None).order_by("?")[
            :3
        ]  # Ordenar aleatoriamente y escoger 3
        return weapons

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["weapons"] = self.get_queryset()
        return context


class EquipWeapon(LoginRequiredMixin, UpdateView):
    model = Character
    fields = []
    template_name = "tierra_media/equip_weapon.html"
    context_object_name = "objects"

    def get_success_url(self):
        return reverse_lazy(
            "tierra_media:character_details", kwargs={"pk": self.get_object().pk}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        character = self.get_object()
        backpack = Backpack.objects.get(owner=character.pk)
        weapons = Weapon.objects.filter(user=self.request.user, backpack=backpack)
        armors = Armor.objects.filter(user=self.request.user, backpack=backpack)
        context["weapons"] = weapons
        context["armors"] = armors
        return context

    def post(self, request, *args, **kwargs):
        character = self.get_object()
        if "weapon" in request.POST:
            item_selected = request.POST.get("weapon")
            item_found = Weapon.objects.get(pk=item_selected)
            print(item_found)
            character.equipped_weapon = item_found
            character.save()
            messages.success(request, "Arma equipada con éxito")
            return redirect(self.get_success_url())

        item_selected = request.POST.get("armor")
        item_found = Armor.objects.get(pk=item_selected)
        character.equipped_armor = item_found
        character.save()
        messages.success(request, "Armadura equipada con éxito")
        return redirect(self.get_success_url())


class Shop(LoginRequiredMixin, TemplateView):
    template_name = "tierra_media/shop.html"


class Move(LoginRequiredMixin, UpdateView):
    model = Character
    fields = []
    template_name = "move/move.html"
    context_object_name = "character"

    def get_success_url(self):
        return reverse_lazy("tierra_media:move_success", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        character = self.get_object()
        context["locations"] = Location.objects.exclude(id=character.location.id)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        character = self.get_object()
        new_location_id = request.POST.get("location")

        new_location = Location.objects.filter(id=new_location_id).first()

        if new_location:
            character.location = new_location
            character.save()
            messages.success(request, "Ubicación cambiada con éxito.")
            return redirect(self.get_success_url())

        messages.error(request, "Ocurrió un error al intentar cambiar la ubicación.")
        return redirect(self.get_success_url())


class MoveSuccess(LoginRequiredMixin, TemplateView):
    template_name = "move/success.html"
