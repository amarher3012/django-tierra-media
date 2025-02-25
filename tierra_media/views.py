import random
from django.contrib.admin import action
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.core.files import File
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.utils.http import urlencode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import CustomUserCreationForm, CreateCharacterForm
from .models import Character, Weapon, Armor, Location, Faction, Race, Backpack
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import *
from django.forms.models import model_to_dict
from .constants import npc_init, weapons_init, armors_init


class RegisterView(FormView):
    template_name = "registration/signin.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("tierra_media:login")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        token = default_token_generator.make_token(user)

        uid = user.pk

        token_url = self.build_activation_url(uid, token)

        self.send_activation_email(user, token_url)

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
        context['active_page'] = 'index'
        return context


class InfoView(TemplateView):
    template_name = "nav/info.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_page'] = 'info'
        return context

class ContactView(FormView):
    pass

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

    @method_decorator(cache_page(60*5))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

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


class Shop(LoginRequiredMixin, UpdateView):
    model = Character
    fields = []
    template_name = "tierra_media/shop.html"
    context_object_name = "objects"

    def get_success_url(self):
        return reverse_lazy(
            "tierra_media:character_details", kwargs={"pk": self.get_object().pk}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        weapons = Weapon.objects.filter(user=self.request.user, backpack=None)
        armors = Armor.objects.filter(user=self.request.user, backpack=None)
        context["weapons"] = weapons
        context["armors"] = armors
        return context

    def post(self, request, *args, **kwargs):
        character = self.get_object()
        backpack = Backpack.objects.get(owner=character.pk)
        if 'weapon' in request.POST:
            item_selected = request.POST.get("weapon")
            print(item_selected)
            item_found = Weapon.objects.get(pk=item_selected)
            item_found.backpack = backpack
            item_found.save()
            messages.success(request,f'{item_found.name} enviado al inventario')
            return redirect(self.get_success_url())

        item_selected = request.POST.get("armor")
        item_found = Armor.objects.get(pk=item_selected)
        item_found.backpack = backpack
        item_found.save()
        messages.success(request, f'{item_found.name} enviado al inventario')
        return redirect(self.get_success_url())

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


class Encounter(LoginRequiredMixin, TemplateView):
    template_name = "encounters/encounters.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        character_id = self.kwargs.get("pk")

        try:
            # Obtener el personaje del usuario actual
            character = Character.objects.select_related(
                "location", "faction", "race"
            ).get(pk=character_id, user=self.request.user)
            location = character.location

            # Filtrar los encuentros para que solo sean personajes del usuario actual
            encounters = (
                Character.objects.select_related("faction", "race")
                .filter(
                    location=location, user=self.request.user
                )  # Solo personajes del usuario actual
                .exclude(pk=character_id)  # Excluir al personaje actual
            )

            faction = character.faction.name
            relationships = {"allies": [], "enemies": [], "neutrals": []}

            for encounter in encounters:
                encounter_faction = encounter.faction.name

                match faction:
                    case "La Comunidad del Anillo":
                        match encounter_faction:
                            case "La Comunidad del Anillo" | "Rivendel":
                                relationships["allies"].append(encounter)
                            case "Isengard" | "Mordor":
                                relationships["enemies"].append(encounter)
                            case _:
                                relationships["neutrals"].append(encounter)

                    case "Isengard" | "Mordor":
                        match encounter_faction:
                            case "Isengard" | "Mordor":
                                relationships["allies"].append(encounter)
                            case _:
                                relationships["enemies"].append(encounter)

                    case "Rivendel":
                        match encounter_faction:
                            case "Rivendel" | "La Comunidad del Anillo":
                                relationships["allies"].append(encounter)
                            case "Isengard" | "Mordor":
                                relationships["enemies"].append(encounter)
                            case _:
                                relationships["neutrals"].append(encounter)

                    case "Lothlorien":
                        match encounter_faction:
                            case "Lothlorien":
                                relationships["allies"].append(encounter)
                            case "Isengard" | "Mordor":
                                relationships["enemies"].append(encounter)
                            case _:
                                relationships["neutrals"].append(encounter)

            context["character"] = character
            context["location"] = location
            context["relationships"] = relationships

        except Character.DoesNotExist:
            messages.error(self.request, "El personaje no existe.")
            context["relationships"] = {"allies": [], "enemies": [], "neutrals": []}

        return context


class EncounterAlly(LoginRequiredMixin, UpdateView):
    template_name = "encounters/ally.html"
    model = Character
    context_object_name = "character"
    fields = []

    def get_object(self):
        return get_object_or_404(
            Character, pk=self.kwargs["pk"], user=self.request.user
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        character = self.get_object()
        ally_id = self.kwargs.get("ally_id")
        ally = get_object_or_404(Character, pk=ally_id)
        decline = False
        crit_healing = False
        healing_amount = 0
        weapon = False
        gift = None

        # Si la vida del personaje utilizado está por debajo del 50%, entonces será más probable que nos ofrezcan curación.
        if character.health < character.max_health / 2:
            healing = random.choices([True, False], weights=[75, 25])[0]
        else:
            healing = random.choice([True, False])

        # Si el personaje va a recibir curación pero ya se encuentra con la vida máxima,
        if healing and character.health == character.max_health:
            decline = True

        if healing:
            crit_healing = random.choices([True, False], weights=[10, 90])[0]

            if crit_healing:
                character.health = character.max_health
                character.save()
            else:
                healing_amount = random.randrange(10, 100)
                # Con min nos encargamos de que la vida actual no supere la vida máxima del personaje.
                healed_amount = min(
                    character.health + healing_amount, character.max_health
                )
                character.health = healed_amount
                character.save()
        else:
            gift_is_weapon = random.choice([True, False])

            if gift_is_weapon:
                gift = (
                    Weapon.objects.filter(user=self.request.user, backpack=None)
                    .order_by("?")
                    .first()
                )
                weapon = True
            else:
                gift = (
                    Armor.objects.filter(user=self.request.user, backpack=None)
                    .order_by("?")
                    .first()
                )

            if gift:
                gift.backpack = character.backpack
                gift.save()

        context["healing"] = healing
        context["crit_healing"] = crit_healing
        context["healing_amount"] = healing_amount
        context["decline"] = decline
        context["weapon"] = weapon
        context["ally"] = ally
        context["gift"] = gift
        context["character"] = character
        return context

    def get_success_url(self):
        return reverse_lazy("encounters:encounter", kwargs={"pk": self.object.pk})


class EncounterNeutral(LoginRequiredMixin, TemplateView):
    template_name = "encounters/neutral.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        character_id = self.kwargs.get("pk")
        neutral_id = self.kwargs.get("neutral_id")

        context["character"] = get_object_or_404(
            Character, pk=character_id, user=self.request.user
        )
        context["neutral"] = get_object_or_404(Character, pk=neutral_id)
        context["encounter"] = context["neutral"]
        return context


class CombatManager:
    def __init__(self, character, enemy, request=None):
        self.character = character
        self.enemy = enemy
        self.request = request

        # Inicializar estados de defensa
        self.character.critical_defense = False
        self.enemy.critical_defense = False
        self.character.defense_reduction = 0
        self.enemy.defense_reduction = 0

    def calculate_damage(self, attacker, defender):
        """Calcula el daño infligido por el atacante al defensor con valores más altos."""
        # Verificar si el atacante tiene un arma equipada
        if not attacker.equipped_weapon:
            return 0

        # Verificar si el defensor tiene defensa crítica activada
        if hasattr(defender, 'critical_defense') and defender.critical_defense:
            return 0

        # Obtener el daño base del arma y aplicar un multiplicador general para aumentar el daño
        # CAMBIO: Multiplicador de daño base para aumentar todos los daños
        base_damage_multiplier = 2.5  # Multiplicador para escalar el daño
        weapon_damage = attacker.equipped_weapon.damage * base_damage_multiplier

        # Añadir daño base adicional independiente del arma
        # CAMBIO: Añadir un daño base adicional
        additional_base_damage = 10
        weapon_damage += additional_base_damage

        # Obtener bonificaciones raciales del atacante
        racial_bonus = self.get_racial_bonus(attacker)

        # Aplicar multiplicador de daño racial
        weapon_damage = int(weapon_damage * racial_bonus["damage_multiplier"])

        # Calcular defensa total del defensor
        defense = defender.defense
        if defender.equipped_armor:
            defense += defender.equipped_armor.defense

        # Aplicar bonificaciones de defensa raciales al defensor
        defense_multiplier = self.get_racial_bonus(defender)["defense_multiplier"]
        defense = int(defense * defense_multiplier)

        # CAMBIO: Ajustar el cálculo de la reducción de daño para que la defensa tenga menos impacto
        # y permita daños más altos mientras sigue siendo relevante
        defense_percentage = min(defense / 300, 0.65)  # Máximo 65% de reducción (antes era 80%)

        # Aplicar reducción de daño si el defensor está en posición defensiva
        if hasattr(defender, 'defense_reduction') and defender.defense_reduction > 0:
            weapon_damage = int(weapon_damage * (1 - defender.defense_reduction))

        # El daño final es el daño del arma menos la defensa porcentual (mínimo 1)
        final_damage = max(int(weapon_damage * (1 - defense_percentage)), 1)

        # CAMBIO: Añadir variabilidad al daño final con un factor aleatorio
        damage_variance = random.uniform(0.9, 1.3)  # -10% a +30% de variación
        final_damage = int(final_damage * damage_variance)

        return final_damage

    def perform_attack(self, attacker, defender):
        """Realiza un ataque y devuelve el daño infligido."""
        # Verificar si el atacante tiene un arma equipada
        if not attacker.equipped_weapon:
            # Mensaje personalizado cuando el atacante no tiene arma
            if attacker == self.character:
                message = f"Al estar desarmado, apenas puedes acercarte a {defender.name} antes de caer derrotado."
            else:
                # Mensaje para cuando el enemigo está desarmado
                message = f"{attacker.name} está desarmado y es derrotado rápidamente."

            # El atacante pierde automáticamente por no tener arma (marcamos como sin salud)
            attacker.health = 0
            attacker.save()

            return {
                "action": "attack",
                "damage": 0,
                "crit": False,
                "attacker": attacker.name,
                "defender": defender.name,
                "message": message  # Incluir el mensaje en el resultado
            }

        # Verificar si el defensor no tiene arma equipada
        # (esto es para cuando el personaje ataca a un enemigo desarmado)
        if defender == self.enemy and not defender.equipped_weapon:
            message = f"{defender.name} está desarmado y es derrotado rápidamente."

            # El defensor pierde automáticamente por no tener arma (marcamos como sin salud)
            defender.health = 0
            defender.save()

            return {
                "action": "attack",
                "damage": 0,
                "crit": False,
                "attacker": attacker.name,
                "defender": defender.name,
                "message": message  # Incluir el mensaje en el resultado
            }

        # Calcular si el ataque es crítico
        attacker_bonus = self.get_racial_bonus(attacker)

        # Calcular la probabilidad de crítico (base + bono racial)
        crit_chance = 15  # Probabilidad base de crítico (15%)
        crit_chance += attacker_bonus["crit"]  # Sumar el bono de crítico racial

        # Calcular si el ataque es crítico
        crit = random.choices([True, False], weights=[crit_chance, 100 - crit_chance])[0]

        # Calcular el daño base usando el método de cálculo
        base_damage = self.calculate_damage(attacker, defender)

        # Aplicar multiplicador de daño crítico si corresponde
        damage = int(base_damage * 1.5) if crit else base_damage

        # Reducir la salud del defensor (asegurando que no sea negativa)
        defender.health = max(defender.health - damage, 0)
        defender.save()

        # Retornar el resultado del ataque
        return {
            "action": "attack",
            "damage": damage,
            "crit": crit,
            "attacker": attacker.name,
            "defender": defender.name,
        }

    def perform_defend(self, defender):
        """Prepara la defensa del defensor con valores más robustos."""
        # Aumentar la probabilidad de defensa crítica
        crit_chance = 25 + (defender.defense * 0.12)  # Antes 22%
        crit_chance = min(crit_chance, 100)

        crit_defense = random.choices(
            [True, False], weights=[crit_chance, 100 - crit_chance]
        )[0]

        if crit_defense:
            # Defensa crítica: anula todo el daño
            defender.critical_defense = True
            defender.defense_reduction = 1.0

            # Aumentar el bono de defensa para defensas críticas
            defense_bonus = defender.defense * 4  # Antes era 3
            return {
                "action": "defend",
                "crit_defense": True,
                "defense_reduction": 1.0,
                "defense_bonus": defense_bonus
            }
        else:
            # Aumentar la reducción de daño para defensa normal
            defender.defense_reduction = 0.6  # Antes 0.45 (45% → 60%)
            defender.critical_defense = False

            # Aumentar el bono de defensa para defensas normales
            defense_bonus = int(defender.defense * 0.8)  # Antes 0.5
            return {
                "action": "defend",
                "crit_defense": False,
                "defense_reduction": 0.6,
                "defense_bonus": defense_bonus
            }

    def calculate_damage(self, attacker, defender):
        """Calcula el daño infligido por el atacante al defensor con mejor defensa."""
        # Verificar si el atacante tiene un arma equipada
        if not attacker.equipped_weapon:
            return 0

        # Verificar si el defensor tiene defensa crítica activada
        if hasattr(defender, 'critical_defense') and defender.critical_defense:
            return 0

        # Obtener el daño base del arma y aplicar un multiplicador general para aumentar el daño
        base_damage_multiplier = 2.5
        weapon_damage = attacker.equipped_weapon.damage * base_damage_multiplier

        # Añadir daño base adicional independiente del arma
        additional_base_damage = 10
        weapon_damage += additional_base_damage

        # Obtener bonificaciones raciales del atacante
        racial_bonus = self.get_racial_bonus(attacker)

        # Aplicar multiplicador de daño racial
        weapon_damage = int(weapon_damage * racial_bonus["damage_multiplier"])

        # Calcular defensa total del defensor
        defense = defender.defense
        if defender.equipped_armor:
            defense += defender.equipped_armor.defense

        # Aplicar bonificaciones de defensa raciales al defensor
        defense_multiplier = self.get_racial_bonus(defender)["defense_multiplier"]
        defense = int(defense * defense_multiplier)

        # CAMBIO: Mejorar la reducción de daño por defensa
        defense_percentage = min(defense / 250, 0.75)  # Máximo 75% de reducción (antes era 65%)

        # Aplicar reducción de daño si el defensor está en posición defensiva
        if hasattr(defender, 'defense_reduction') and defender.defense_reduction > 0:
            weapon_damage = int(weapon_damage * (1 - defender.defense_reduction))

        # El daño final es el daño del arma menos la defensa porcentual (mínimo 1)
        final_damage = max(int(weapon_damage * (1 - defense_percentage)), 1)

        # Añadir variabilidad al daño final con un factor aleatorio
        damage_variance = random.uniform(0.9, 1.3)  # -10% a +30% de variación
        final_damage = int(final_damage * damage_variance)

        return final_damage

    def perform_flee(self, flee_chance, character, opponent):
        """Intenta huir y devuelve si tuvo éxito."""
        # Probabilidad base de huir (50%)
        base_flee_chance = 50

        # Obtener bonos raciales
        char_bonus = self.get_racial_bonus(character)

        # Aplicar bonificación racial
        base_flee_chance += char_bonus["flee_chance"]

        # Aumentar la dificultad si el oponente es un orco
        if opponent.race.name == "Orco":
            base_flee_chance -= 20  # Reducir la probabilidad de huir en 20%

        # Asegurarse de que la probabilidad esté entre 0 y 100
        base_flee_chance = max(min(base_flee_chance, 100), 0)

        # Intentar huir
        flee_success = random.choices(
            [True, False], weights=[base_flee_chance, 100 - base_flee_chance]
        )[0]

        return flee_success

    def get_racial_bonus(self, character):
        """Devuelve los bonos raciales para iniciativa, daño y defensa."""
        bonuses = {
            "initiative": 0,
            "damage_multiplier": 1.0,
            "defense_multiplier": 1.0,
            "flee_chance": 0,
            "crit": 0,
        }

        # Verificar que character.race existe
        if not hasattr(character, 'race') or not character.race:
            return bonuses

        race_name = character.race.name

        if race_name == "Humano":
            bonuses["initiative"] += 5
            bonuses["damage_multiplier"] = 1.20
        elif race_name == "Elfo":
            bonuses["initiative"] += 20
            bonuses["damage_multiplier"] = 1.10
            bonuses["crit"] = 15
        elif race_name == "Enano":
            bonuses["defense_multiplier"] = 1.20
            bonuses["damage_multiplier"] = 1.10
        elif race_name == "Hobbit":
            bonuses["flee_chance"] += 20
            bonuses["initiative"] += 15
        elif race_name == "Orco":
            bonuses["damage_multiplier"] = 1.50

        return bonuses

    def reset_defense_after_turn(self):
        """Restaura el estado de defensa después de un turno de combate."""
        # Eliminar el estado de defensa crítica
        self.character.critical_defense = False
        self.enemy.critical_defense = False

        # Eliminar la reducción de daño por defensa
        if hasattr(self.character, 'defense_reduction'):
            self.character.defense_reduction = 0

        if hasattr(self.enemy, 'defense_reduction'):
            self.enemy.defense_reduction = 0

    def combat_turn(self, action):
        """Maneja un turno de combate."""
        # IMPORTANTE: Restaurar la defensa a su valor original al inicio de cada turno
        # Esta línea es crucial para evitar que la defensa se acumule infinitamente
        self.reset_defense_after_turn()

        # Log para depuración
        print(f"Defensas restablecidas: Character={self.character.defense}, Enemy={self.enemy.defense}")

        # Manejar la acción de huir
        if action == "flee":
            flee_success = self.perform_flee(20, self.character, self.enemy)

            # Si el intento de huida falla, el enemigo ataca
            if not flee_success:
                # El enemigo ataca
                enemy_attack_result = self.perform_attack(self.enemy, self.character)
                enemy_damage = enemy_attack_result["damage"]
                enemy_crit = enemy_attack_result["crit"]

                # Crear mensaje sobre el ataque del enemigo
                if enemy_crit:
                    enemy_message = f"¡No has logrado huir! {self.enemy.name} te ha hecho un golpe crítico de {enemy_damage} puntos de daño."
                else:
                    enemy_message = f"¡No has logrado huir! {self.enemy.name} te ha atacado y te ha hecho {enemy_damage} puntos de daño."

                # Determinar el resultado final
                message_tag = "danger"
                outcome = None

                if self.character.health <= 0:
                    enemy_message += f" ¡Has sido derrotado por {self.enemy.name}!"
                    outcome = "defeat"
                    # No eliminamos al personaje, solo lo marcamos como derrotado

                result = {
                    "action": "flee",
                    "success": flee_success,
                    "message": enemy_message,
                    "message_tag": message_tag,
                    "outcome": outcome,
                    "character_id": self.character.pk  # Añadir ID del personaje
                }
            else:
                # Si la huida tiene éxito, solo retornar el mensaje de éxito
                result = {
                    "action": "flee",
                    "success": flee_success,
                    "message": "¡Has logrado huir!",
                    "message_tag": "success",
                    "outcome": "flee",
                    "character_id": self.character.pk  # Añadir explícitamente el ID del personaje aquí
                }

        # Manejar la acción de defenderse
        elif action == "defend":
            # El personaje se defiende
            defense_result = self.perform_defend(self.character)

            # Mensaje según el resultado
            if defense_result["crit_defense"]:
                message = f"¡{self.character.name} ha realizado una defensa crítica y no recibirá daño este turno!"
            else:
                # Usar get() para evitar KeyError si defense_bonus no está en el resultado
                defense_bonus = defense_result.get("defense_bonus", int(self.character.defense * 0.3))
                message = f"¡{self.character.name} se pone en posición defensiva y aumenta su defensa en {defense_bonus} puntos para este turno!"

            # El enemigo también toma su decisión
            if self.enemy.health <= (self.enemy.max_health * 0.5) and random.random() < 0.33:
                enemy_action = "defend"
                enemy_defense_result = self.perform_defend(self.enemy)

                # Actualizar mensaje
                if enemy_defense_result["crit_defense"]:
                    message += f" ¡{self.enemy.name} también ha ejecutado una defensa crítica!"
                else:
                    # Usar get() para evitar KeyError
                    enemy_defense_bonus = enemy_defense_result.get("defense_bonus", int(self.enemy.defense * 0.3))
                    message += f" ¡{self.enemy.name} también ha aumentado su defensa en {enemy_defense_bonus} puntos!"
            else:
                # El enemigo decide atacar - SIEMPRE DESPUÉS de que el personaje se defienda
                enemy_action = "attack"
                enemy_attack_result = self.perform_attack(self.enemy, self.character)
                enemy_damage = enemy_attack_result["damage"]
                enemy_crit = enemy_attack_result["crit"]

                # Agregar al mensaje - el ataque ocurre después de la defensa
                if enemy_crit:
                    message += f" ¡Después de tu defensa, {self.enemy.name} te ha hecho un golpe crítico de {enemy_damage} puntos de daño!"
                else:
                    message += f" Después de tu defensa, {self.enemy.name} te ha atacado y te ha hecho {enemy_damage} puntos de daño."

            # Establecer el tipo de mensaje y verificar el resultado
            message_tag = "warning"  # Cambié a "warning" para que coincida con el color del botón
            outcome = None

            if self.character.health <= 0:
                message += f" ¡Has sido derrotado por {self.enemy.name}!"
                message_tag = "danger"
                outcome = "defeat"
                # No eliminamos al personaje, solo lo marcamos como derrotado
            elif self.enemy.health <= 0:
                message += f" ¡Has derrotado a {self.enemy.name}!"
                message_tag = "success"
                outcome = "victory"
                # No eliminamos al enemigo, solo lo marcamos como derrotado

            result = {
                "action": "defend",
                "message": message,
                "message_tag": message_tag,
                "outcome": outcome,
                "character_id": self.character.pk  # Asegurar que siempre se incluya
            }

        # Manejar la acción de atacar
        elif action == "attack":
            # El personaje ataca primero siempre
            character_attack_result = self.perform_attack(self.character, self.enemy)

            # Verificar si el personaje no tenía arma
            if not self.character.equipped_weapon:
                # Usar el mensaje personalizado del resultado
                message = character_attack_result.get("message",
                                                      f"Al estar desarmado, apenas puedes acercarte a {self.enemy.name} antes de caer derrotado.")
                message_tag = "danger"
                outcome = "defeat"

                # En lugar de eliminar, marcamos el personaje como completamente sin salud
                self.character.health = 0
                self.character.save()

                result = {
                    "action": "attack",
                    "message": message,
                    "message_tag": message_tag,
                    "outcome": outcome,
                    "character_id": self.character.pk
                }

            # Verificar si el enemigo no tenía arma o ha sido derrotado
            elif not self.enemy.equipped_weapon or self.enemy.health <= 0:
                # Si el enemigo estaba desarmado o ha sido derrotado, verificamos el mensaje
                if character_attack_result.get("message") and "desarmado" in character_attack_result.get(
                        "message") or self.enemy.health <= 0:
                    message = character_attack_result.get("message") or f"Has derrotado a {self.enemy.name}."
                    message_tag = "success"
                    outcome = "victory"

                    # En lugar de eliminar, marcamos el enemigo como completamente sin salud
                    self.enemy.health = 0
                    self.enemy.save()

                    result = {
                        "action": "attack",
                        "message": message,
                        "message_tag": message_tag,
                        "outcome": outcome,
                        "character_id": self.character.pk,
                        "enemy_name": self.enemy.name
                    }

                else:
                    # Continuar con el flujo normal si hay algo inesperado
                    character_damage = character_attack_result["damage"]
                    character_crit = character_attack_result["crit"]

                    # Construir mensaje para el ataque del personaje
                    if character_crit:
                        message = f"¡Has realizado un golpe crítico! Has infligido {character_damage} puntos de daño a {self.enemy.name}."
                    else:
                        message = f"Has atacado y has infligido {character_damage} puntos de daño a {self.enemy.name}."

                    # Verificar si el enemigo ha sido derrotado
                    if self.enemy.health <= 0:
                        message += f" ¡Has derrotado a {self.enemy.name}!"
                        message_tag = "success"
                        outcome = "victory"

                        result = {
                            "action": "attack",
                            "message": message,
                            "message_tag": message_tag,
                            "outcome": outcome,
                            "character_id": self.character.pk
                        }
                    else:
                        # Si el enemigo sigue vivo, contraataca
                        enemy_attack_result = self.perform_attack(self.enemy, self.character)
                        enemy_damage = enemy_attack_result["damage"]
                        enemy_crit = enemy_attack_result["crit"]

                        if enemy_crit:
                            message += f" ¡En respuesta, {self.enemy.name} te ha hecho un golpe crítico de {enemy_damage} puntos de daño!"
                        else:
                            message += f" En respuesta, {self.enemy.name} te ha atacado y te ha hecho {enemy_damage} puntos de daño."

                        # Determinar el resultado final
                        message_tag = "danger"
                        outcome = None

                        if self.character.health <= 0:
                            message += f" ¡Has sido derrotado por {self.enemy.name}!"
                            outcome = "defeat"

                        result = {
                            "action": "attack",
                            "message": message,
                            "message_tag": message_tag,
                            "outcome": outcome,
                            "character_id": self.character.pk
                        }
            else:
                # Continuar con el flujo normal si ambos tienen arma
                character_damage = character_attack_result["damage"]
                character_crit = character_attack_result["crit"]

                # Construir mensaje para el ataque del personaje
                if character_crit:
                    message = f"¡Has realizado un golpe crítico! Has infligido {character_damage} puntos de daño a {self.enemy.name}."
                else:
                    message = f"Has atacado y has infligido {character_damage} puntos de daño a {self.enemy.name}."

                # Verificar si el enemigo ha sido derrotado
                if self.enemy.health <= 0:
                    message += f" ¡Has derrotado a {self.enemy.name}!"
                    message_tag = "success"
                    outcome = "victory"

                    result = {
                        "action": "attack",
                        "message": message,
                        "message_tag": message_tag,
                        "outcome": outcome,
                        "character_id": self.character.pk
                    }
                else:
                    # Si el enemigo sigue vivo, contraataca
                    enemy_attack_result = self.perform_attack(self.enemy, self.character)
                    enemy_damage = enemy_attack_result["damage"]
                    enemy_crit = enemy_attack_result["crit"]

                    if enemy_crit:
                        message += f" ¡En respuesta, {self.enemy.name} te ha hecho un golpe crítico de {enemy_damage} puntos de daño!"
                    else:
                        message += f" En respuesta, {self.enemy.name} te ha atacado y te ha hecho {enemy_damage} puntos de daño."

                    # Determinar el resultado final
                    message_tag = "danger"
                    outcome = None

                    if self.character.health <= 0:
                        message += f" ¡Has sido derrotado por {self.enemy.name}!"
                        outcome = "defeat"

                    result = {
                        "action": "attack",
                        "message": message,
                        "message_tag": message_tag,
                        "outcome": outcome,
                        "character_id": self.character.pk
                    }
        else:
            # Si llegamos aquí, algo salió mal
            result = {
                "action": "error",
                "message": "Acción no reconocida",
                "message_tag": "danger",
                "character_id": self.character.pk  # Añadir ID del personaje incluso en caso de error
            }

        # Verificar si hay que eliminar el enemigo (añadir al final del método)
        enemy_defeated = False

        # Si el resultado contiene un outcome de victoria
        if result.get('outcome') == 'victory':
            enemy_defeated = True

        # O si la salud del enemigo es 0 o menos
        elif self.enemy.health <= 0:
            enemy_defeated = True

        # Si el enemigo está derrotado y es un NPC, eliminarlo
        if enemy_defeated and self.enemy.npc:
            try:
                # Guardar el ID y nombre para logueo
                enemy_id = self.enemy.pk
                enemy_name = self.enemy.name

                # Eliminar el enemigo
                self.enemy.delete()
                print(f"Enemigo {enemy_name} (ID: {enemy_id}) eliminado de la base de datos.")
            except Exception as e:
                print(f"Error al eliminar al enemigo: {e}")

        return result


class EncounterEnemy(LoginRequiredMixin, TemplateView):
    template_name = "encounters/enemy.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        character_id = self.kwargs.get("pk")
        enemy_id = self.kwargs.get("enemy_id")

        character = get_object_or_404(Character, pk=character_id, user=self.request.user)
        enemy = get_object_or_404(Character, pk=enemy_id)

        has_weapon = character.equipped_weapon is not None

        context["character"] = character
        context["enemy"] = enemy
        context["has_weapon"] = has_weapon
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        character_id = self.kwargs.get("pk")
        enemy_id = self.kwargs.get("enemy_id")

        character = get_object_or_404(Character, pk=character_id, user=request.user)
        enemy = get_object_or_404(Character, pk=enemy_id)

        action = request.POST.get("action")

        print(f"Acción recibida: {action}")
        print(f"Personaje: {character.name}, Salud: {character.health}, Defensa: {character.defense}")
        print(f"Enemigo: {enemy.name}, Salud: {enemy.health}, Defensa: {enemy.defense}")

        if action not in ["attack", "defend", "flee"]:
            return JsonResponse({
                "status": "error",
                "message": "Acción no válida.",
                "character_id": character.pk
            })

        # Crear el gestor de combate
        combat_manager = CombatManager(character, enemy, request)

        # Ejecutar el turno de combate
        result = combat_manager.combat_turn(action)

        print(f"Resultado del turno: {result}")

        # Obtener el mensaje y tipo de alerta
        message = result.get("message", "")
        message_tag = result.get("message_tag", "info")
        outcome = result.get("outcome")

        # Refrescar los objetos desde la base de datos para obtener los valores actualizados
        try:
            character_refreshed = Character.objects.get(pk=character_id)
            character_health = character_refreshed.health
            character_max_health = character_refreshed.max_health
            character_defense = character_refreshed.defense
        except Character.DoesNotExist:
            # Si el personaje ya no existe, usamos los valores anteriores
            character_health = 0
            character_max_health = character.max_health
            character_defense = character.defense

        try:
            enemy_refreshed = Character.objects.get(pk=enemy_id)
            enemy_health = enemy_refreshed.health
            enemy_max_health = enemy_refreshed.max_health
            enemy_defense = enemy_refreshed.defense
        except Character.DoesNotExist:
            # Si el enemigo ya no existe, usamos los valores anteriores
            enemy_health = 0
            enemy_max_health = enemy.max_health
            enemy_defense = enemy.defense

        # Preparar la respuesta JSON
        response_data = {
            "status": "success",
            "message": message,
            "message_tag": message_tag,
            "action": result.get("action"),
            "character_id": character_id,
            "enemy_name": enemy.name,
            "success": result.get("success", False) if action == "flee" else None,
            "outcome": outcome,
            "character_health": character_health,
            "character_max_health": character_max_health,
            "character_defense": character_defense,
            "enemy_health": enemy_health,
            "enemy_max_health": enemy_max_health,
            "enemy_defense": enemy_defense
        }

        return JsonResponse(response_data)