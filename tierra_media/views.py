import random

from django.contrib.admin import action
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import JsonResponse
from django.utils.http import urlencode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.conf import settings
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import *
from .forms import CustomUserCreationForm
from .forms import CreateCharacterForm
from django.forms.models import model_to_dict
from .models import (
    Character,
    Weapon,
    Armor,
    Location,
    Faction,
    Race,
    Relationship,
    Backpack,
)
from .constants import npc_init, weapons_init, armors_init


@receiver(post_save, sender=Character)
def create_backpack_for_character(sender, instance, created, **kwargs):
    if created:
        # Crear un backpack vacío para el personaje recién creado
        Backpack.objects.create(owner=instance)


@receiver(post_save, sender=Character)
def save_backpack_for_character(sender, instance, **kwargs):
    # Asegurarse de que el backpack del personaje se guarda
    instance.backpack.save()


class RegisterView(FormView):
    template_name = "registration/signin.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("tierra_media:index")

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


class IndexView(LoginRequiredMixin, ListView):
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
    success_url = "/tierra-media/character-creation/success/"

    def check_name(self, form):
        name = form.cleaned_data.get("name")
        user = self.request.user

        if Character.objects.filter(name=name, user=user).exists():
            form.add_error("name", "Ya tienes un personaje con ese nombre.")
            return False
        return True

    def form_valid(self, form):
        if self.check_name(form):
            form.instance.user = self.request.user
            messages.success(self.request, "Personaje creado con éxito.")
            return super().form_valid(form)

        messages.error(self.request, "Ocurrió un error al intentar crear el personaje.")
        return super().form_invalid(form)


class CharacterCreationSuccess(TemplateView):
    template_name = "character-creation/success.html"


class NPC_preparations:
    def create_npcs(user):
        npcs = npc_init()
        for npc in npcs:
            faction_name = npc.pop("faction")
            location_name = npc.pop("location")
            race_name = npc.pop("race")

            faction = Faction.objects.get(name__iexact=faction_name)
            location = Location.objects.get(name__iexact=location_name)
            race = Race.objects.get(name__iexact=race_name)

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


class WeaponPreparations:
    def create_weapons(user):
        weapons = weapons_init()
        for weapon in weapons:
            weapon.update(
                {
                    "user": user,
                }
            )
            weapon_object = Weapon(**weapon)
            weapon_object.save()


class CharacterDetailsView(LoginRequiredMixin, DetailView):
    model = Character
    template_name = "tierra_media/character_menu.html"
    context_object_name = "character"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        character = self.get_object()
        context["character"] = model_to_dict(character, exclude=["user"])

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


class ArmorPreparations:
    def create_armors(user):
        armors = armors_init()
        for armor in armors:
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


class EquipWeapon(LoginRequiredMixin, TemplateView):
    template_name = "tierra_media/equip_weapon.html"


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
            if self.request:
                messages.error(self.request, f"{attacker.name} no tenía un arma equipada y ha perdido automáticamente.")
            defender.health = 0
            defender.save()
            return {
                "action": "attack",
                "damage": 0,
                "crit": False,
                "attacker": attacker.name,
                "defender": defender.name,
            }

        # Calcular si el ataque es crítico
        attacker_bonus = self.get_racial_bonus(attacker)

        # CAMBIO: Aumentar ligeramente la probabilidad base de crítico
        crit_chance = 18  # Probabilidad base de crítico (antes 15%)
        crit_chance += attacker_bonus["crit"]

        # Calcular si el ataque es crítico
        crit = random.choices([True, False], weights=[crit_chance, 100 - crit_chance])[0]

        # Calcular el daño base
        base_damage = self.calculate_damage(attacker, defender)

        # CAMBIO: Aumentar el multiplicador de daño crítico
        crit_multiplier = 1.8  # Antes era 1.5
        damage = int(base_damage * crit_multiplier) if crit else base_damage

        # Reducir la salud del defensor
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
        """Prepara la defensa del defensor con valores mejorados."""
        # CAMBIO: Aumentar ligeramente la probabilidad de defensa crítica
        crit_chance = 22 + (defender.defense * 0.1)  # Antes 20%
        crit_chance = min(crit_chance, 100)

        crit_defense = random.choices(
            [True, False], weights=[crit_chance, 100 - crit_chance]
        )[0]

        if crit_defense:
            # Defensa crítica: anula todo el daño
            defender.critical_defense = True
            defender.defense_reduction = 1.0

            # CAMBIO: Aumentar el bono de defensa para defensas críticas
            defense_bonus = defender.defense * 3  # Antes era 2
            return {
                "action": "defend",
                "crit_defense": True,
                "defense_reduction": 1.0,
                "defense_bonus": defense_bonus
            }
        else:
            # CAMBIO: Aumentar la reducción de daño para defensa normal
            defender.defense_reduction = 0.45  # Antes 0.3 (30% → 45%)
            defender.critical_defense = False

            # CAMBIO: Aumentar el bono de defensa para defensas normales
            defense_bonus = int(defender.defense * 0.5)  # Antes 0.3
            return {
                "action": "defend",
                "crit_defense": False,
                "defense_reduction": 0.45,
                "defense_bonus": defense_bonus
            }

    def perform_attack(self, attacker, defender):
        """Realiza un ataque y devuelve el daño infligido."""

        # Verificar si el atacante tiene un arma equipada
        if not attacker.equipped_weapon:
            if self.request:
                messages.error(self.request, f"{attacker.name} no tenía un arma equipada y ha perdido automáticamente.")
            defender.health = 0  # El defensor gana, ya que el atacante no tiene arma
            defender.save()
            return {
                "action": "attack",
                "damage": 0,
                "crit": False,
                "attacker": attacker.name,
                "defender": defender.name,
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
        """Prepara la defensa del defensor.
        Si es crítica, anulará todo el daño.
        Si no, reducirá el daño recibido en un 30%."""

        # Calcular la probabilidad de defensa crítica: 20% base + 10% de la defensa del personaje
        crit_chance = 20 + (defender.defense * 0.1)
        # Asegurar que la probabilidad no exceda el 100%
        crit_chance = min(crit_chance, 100)

        # Determinar si la defensa es crítica basada en la probabilidad calculada
        crit_defense = random.choices(
            [True, False], weights=[crit_chance, 100 - crit_chance]
        )[0]

        if crit_defense:
            # Si la defensa es crítica, el defensor no recibirá daño este turno
            defender.critical_defense = True
            defender.defense_reduction = 1.0  # 100% de reducción
            defense_bonus = defender.defense * 2  # Un bono alto para defensa crítica
            return {
                "action": "defend",
                "crit_defense": True,
                "defense_reduction": 1.0,
                "defense_bonus": defense_bonus
            }
        else:
            # Si la defensa no es crítica, se reducirá el daño recibido en un 30%
            defender.defense_reduction = 0.3  # Reducción del 30%
            defender.critical_defense = False
            defense_bonus = int(defender.defense * 0.3)  # Un bono del 30% para defensa normal
            return {
                "action": "defend",
                "crit_defense": False,
                "defense_reduction": 0.3,
                "defense_bonus": defense_bonus
            }

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
                    self.character.delete()

                return {
                    "action": "flee",
                    "success": flee_success,
                    "message": enemy_message,
                    "message_tag": message_tag,
                    "outcome": outcome,
                    "character_id": self.character.pk  # Añadir ID del personaje
                }
            else:
                # Si la huida tiene éxito, solo retornar el mensaje de éxito
                return {
                    "action": "flee",
                    "success": flee_success,
                    "message": "¡Has logrado huir!",
                    "message_tag": "success",
                    "outcome": "flee",
                    "character_id": self.character.pk  # Añadir explícitamente el ID del personaje aquí
                }

        # Manejar la acción de defenderse
        if action == "defend":
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
                self.character.delete()
            elif self.enemy.health <= 0:
                message += f" ¡Has derrotado a {self.enemy.name}!"
                message_tag = "success"
                outcome = "victory"
                self.enemy.delete()

            return {
                "action": "defend",
                "message": message,
                "message_tag": message_tag,
                "outcome": outcome,
                "character_id": self.character.pk  # Asegurar que siempre se incluya
            }

        # Manejar la acción de atacar
        if action == "attack":
            # El personaje ataca primero siempre
            character_attack_result = self.perform_attack(self.character, self.enemy)
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
                self.enemy.delete()

                return {
                    "action": "attack",
                    "message": message,
                    "message_tag": message_tag,
                    "outcome": outcome,
                    "character_id": self.character.pk  # Añadir ID del personaje
                }

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
                self.character.delete()

            return {
                "action": "attack",
                "message": message,
                "message_tag": message_tag,
                "outcome": outcome,
                "character_id": self.character.pk  # Añadir ID del personaje
            }

        # Si llegamos aquí, algo salió mal
        return {
            "action": "error",
            "message": "Acción no reconocida",
            "message_tag": "danger",
            "character_id": self.character.pk  # Añadir ID del personaje incluso en caso de error
        }


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

        # Guardar el ID del personaje antes de que pueda ser eliminado
        character_id = character.pk

        # Crear el gestor de combate
        combat_manager = CombatManager(character, enemy, request)

        # Ejecutar el turno de combate
        result = combat_manager.combat_turn(action)

        print(f"Resultado del turno: {result}")

        # Obtener el mensaje y tipo de alerta
        message = result.get("message", "")
        message_tag = result.get("message_tag", "info")
        outcome = result.get("outcome")

        # Verificar si hay que redireccionar debido a la eliminación de un personaje
        character_exists = Character.objects.filter(pk=character_id).exists()

        # Preparar la respuesta JSON
        response_data = {
            "status": "success",
            "message": message,
            "message_tag": message_tag,
            "action": result.get("action"),
            "character_id": character_id,
            "success": result.get("success", False) if action == "flee" else None,
            "outcome": outcome
        }

        # Si el personaje aún existe, incluir sus estadísticas actualizadas
        if character_exists:
            character_refreshed = Character.objects.get(pk=character_id)
            response_data.update({
                "character_health": character_refreshed.health,
                "character_max_health": character_refreshed.max_health,
                "character_defense": character_refreshed.defense,
            })
        else:
            # Si el personaje fue eliminado, establecer la salud en 0
            response_data.update({
                "character_health": 0,
                "character_max_health": character.max_health,  # Usar el valor previo
                "character_defense": character.defense,  # Usar el valor previo
            })

        # Comprobar si el enemigo aún existe
        enemy_exists = Character.objects.filter(pk=enemy_id).exists()

        if enemy_exists:
            enemy_refreshed = Character.objects.get(pk=enemy_id)
            response_data.update({
                "enemy_health": enemy_refreshed.health,
                "enemy_max_health": enemy_refreshed.max_health,
                "enemy_defense": enemy_refreshed.defense,
            })
        else:
            # Si el enemigo fue eliminado, establecer la salud en 0
            response_data.update({
                "enemy_health": 0,
                "enemy_max_health": enemy.max_health,  # Usar el valor previo
                "enemy_defense": enemy.defense,  # Usar el valor previo
            })

        return JsonResponse(response_data)