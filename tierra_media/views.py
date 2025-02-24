import random

from django.contrib.admin import action
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.db.models.signals import post_save
from django.dispatch import receiver
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
    def __init__(self, character, enemy):
        self.character = character
        self.enemy = enemy

    def calculate_damage(self, attacker, defender):
        """Calcula el daño infligido por el atacante al defensor."""
        weapon_damage = (
            attacker.equipped_weapon.damage if attacker.equipped_weapon else 0
        )
        defense = defender.defense + (
            defender.equipped_armor.defense if defender.equipped_armor else 0
        )
        return max(weapon_damage - defense, 0)

    def perform_attack(self, attacker, defender):
        """Realiza un ataque y devuelve el daño infligido."""
        damage = self.calculate_damage(attacker, defender)
        defender.health = max(defender.health - damage, 0)
        defender.save()
        return damage

    def perform_defend(self, defender):
        """Aumenta la defensa del defensor y devuelve el bono de defensa."""
        defense_bonus = random.randint(5, 15)
        defender.defense += defense_bonus
        defender.save()
        return defense_bonus

    def perform_flee(self, flee_chance):
        """Intenta huir y devuelve si tuvo éxito."""
        return random.choices([True, False], weights=[flee_chance, 100 - flee_chance])[
            0
        ]

    def get_racial_bonus(self, character):
        """Devuelve los bonos raciales para iniciativa, daño y defensa."""
        bonuses = {
            "initiative": 0,
            "damage_multiplier": 1.0,
            "defense_multiplier": 1.0,
            "flee_chance": 0,
        }

        if character.race.name == "Humano":
            bonuses["initiative"] += 5
            bonuses["damage_multiplier"] = 1.20
        elif character.race.name == "Elfo":
            bonuses["initiative"] += 20
            bonuses["damage_multiplier"] = 1.10
        elif character.race.name == "Enano":
            bonuses["defense_multiplier"] = 1.20
            bonuses["damage_multiplier"] = 1.10
        elif character.race.name == "Hobbit":
            bonuses["flee_chance"] += 20
            bonuses["initiative"] += 15
        elif character.race.name == "Orco":
            bonuses["damage_multiplier"] = 1.50

        return bonuses

    def combat_turn(self, action):
        """Maneja un turno de combate."""
        character_bonus = self.get_racial_bonus(self.character)
        enemy_bonus = self.get_racial_bonus(self.enemy)

        # Determinar quién ataca primero
        character_initiative = 50 + character_bonus["initiative"]
        enemy_initiative = 50 + enemy_bonus["initiative"]
        first = random.choices(
            [True, False], weights=[character_initiative, enemy_initiative]
        )[0]

        active_turn = "character" if first else "enemy"

        while self.character.health > 0 and self.enemy.health > 0:
            if active_turn == "character":
                if action == "defend":
                    defense_bonus = self.perform_defend(self.character)
                    result = {"action": "defend", "defense_bonus": defense_bonus}
                elif action == "flee":
                    flee_success = self.perform_flee(character_bonus["flee_chance"])
                    result = {"action": "flee", "success": flee_success}
                else:
                    damage = self.perform_attack(self.character, self.enemy)
                    result = {"action": "attack", "damage": damage}
            else:
                if self.enemy.health > self.enemy.max_health * 0.5:
                    enemy_action = "attack"
                else:
                    enemy_action = random.choices(
                        ["defend", "attack"], weights=[75, 25]
                    )[0]

                if enemy_action == "defend":
                    defense_bonus = self.perform_defend(self.enemy)
                    result = {
                        "action": "defend",
                        "defense_bonus": defense_bonus,
                        "actor": "enemy",
                    }
                else:
                    damage = self.perform_attack(self.enemy, self.character)
                    result = {"action": "attack", "damage": damage, "actor": "enemy"}

            # Cambiar el turno después de cada acción
            active_turn = "enemy" if active_turn == "character" else "character"

            # Retornar el resultado de la acción actual
            return result

        # Si el bucle termina, el combate ha finalizado
        return {"result": "combat_over"}


class EncounterEnemy(LoginRequiredMixin, TemplateView):
    template_name = "encounters/enemy.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        character_id = self.kwargs.get("pk")
        enemy_id = self.kwargs.get("enemy_id")

        character = get_object_or_404(
            Character, pk=character_id, user=self.request.user
        )
        enemy = get_object_or_404(Character, pk=enemy_id)

        has_weapon = character.equipped_weapon is not None

        context["character"] = character
        context["enemy"] = enemy
        context["has_weapon"] = has_weapon
        return context

    def post(self, request, *args, **kwargs):
        character_id = self.kwargs.get("pk")
        enemy_id = self.kwargs.get("enemy_id")

        character = get_object_or_404(
            Character, pk=character_id, user=self.request.user
        )
        enemy = get_object_or_404(Character, pk=enemy_id)

        action = request.POST.get("action")

        if action not in ["attack", "defend", "flee"]:
            messages.error(request, "Acción no válida.")
            return redirect(
                "tierra_media:encounter_enemy", pk=character_id, enemy_id=enemy_id
            )

        # Inicializar el CombatManager
        combat_manager = CombatManager(character, enemy)

        # Determinar quién ataca primero
        character_bonus = combat_manager.get_racial_bonus(character)
        enemy_bonus = combat_manager.get_racial_bonus(enemy)

        character_initiative = 50 + character_bonus["initiative"]
        enemy_initiative = 50 + enemy_bonus["initiative"]
        first = random.choices(
            [True, False], weights=[character_initiative, enemy_initiative]
        )[0]

        active_turn = "character" if first else "enemy"

        # Bucle de combate
        while character.health > 0 and enemy.health > 0:
            if active_turn == "character":
                # Turno del personaje
                if action == "attack":
                    if not character.equipped_weapon:
                        messages.error(
                            request, "¡Necesitas un arma equipada para atacar!"
                        )
                        return redirect(
                            "tierra_media:encounter_enemy",
                            pk=character_id,
                            enemy_id=enemy_id,
                        )

                    damage = combat_manager.perform_attack(character, enemy)
                    messages.success(
                        request,
                        f"¡Has infligido {damage} puntos de daño a {enemy.name}!",
                    )
                elif action == "defend":
                    defense_bonus = combat_manager.perform_defend(character)
                    messages.info(
                        request, f"¡Has aumentado tu defensa en {defense_bonus} puntos!"
                    )
                elif action == "flee":
                    flee_success = combat_manager.perform_flee(
                        character_bonus["flee_chance"]
                    )
                    if flee_success:
                        messages.success(request, "¡Has logrado huir!")
                        return redirect("tierra_media:index")
                    else:
                        messages.error(request, "¡No has logrado huir!")

            else:
                # Turno del enemigo
                if enemy.health > enemy.max_health * 0.5:
                    enemy_action = "attack"
                else:
                    enemy_action = random.choices(
                        ["defend", "attack"], weights=[75, 25]
                    )[0]

                if enemy_action == "defend":
                    defense_bonus = combat_manager.perform_defend(enemy)
                    messages.warning(
                        request,
                        f"¡{enemy.name} se ha defendido y aumentó su defensa en {defense_bonus} puntos!",
                    )
                else:
                    damage = combat_manager.perform_attack(enemy, character)
                    messages.warning(
                        request,
                        f"¡{enemy.name} te ha infligido {damage} puntos de daño!",
                    )

            active_turn = "enemy" if active_turn == "character" else "character"

            character.save()
            enemy.save()

            if character.health <= 0 or enemy.health <= 0:
                break

        # Verificar el resultado del combate
        if character.health <= 0:
            messages.error(request, "¡Has sido derrotado!")
            character.delete()
            return redirect("tierra_media:index")
        elif enemy.health <= 0:
            messages.success(request, f"¡Has derrotado a {enemy.name}!")
            enemy.delete()
            return redirect("tierra_media:index")

        return redirect(
            "tierra_media:encounter_enemy", pk=character_id, enemy_id=enemy_id
        )
