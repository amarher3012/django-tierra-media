from django.db import models
from django.contrib.auth.models import User
from .constants import FACTION_CHOICES, LOCATION_CHOICES, RACE_CHOICES, SEX_CHOICES
from django.core.exceptions import ValidationError

def validate_character_name(value):
    """
    Validador para nombres de personajes prohibidos.
    """
    forbidden_names = [
        'frodo', 'aragorn', 'legolas', 'gimli', 'sauron',
        'saruman', 'JavaScript', 'Hitler', 'Franco'
    ]

    if value.lower() in [name.lower() for name in forbidden_names]:
        raise ValidationError(
            f"El nombre '{value}' no está permitido para un personaje."
        )


class Faction(models.Model):
    name = models.CharField(max_length=50, choices=FACTION_CHOICES)

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=50, choices=LOCATION_CHOICES)

    def __str__(self):
        return self.name


class Race(models.Model):
    name = models.CharField(max_length=50, choices=RACE_CHOICES)

    def __str__(self):
        return self.name


class Character(models.Model):
    icon = models.ImageField(blank=True, upload_to="uploads/")
    name = models.CharField(max_length=50, validators=[validate_character_name])
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)
    max_health = models.IntegerField(default=250)
    health = models.IntegerField(default=250)
    defense = models.IntegerField(default=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    equipped_weapon = models.OneToOneField(
        "Weapon", on_delete=models.SET_NULL, null=True
    )
    equipped_armor = models.OneToOneField("Armor", on_delete=models.SET_NULL, null=True)
    faction = models.ForeignKey(Faction, on_delete=models.DO_NOTHING)
    location = models.ForeignKey(Location, on_delete=models.DO_NOTHING)
    race = models.ForeignKey(Race, on_delete=models.DO_NOTHING)
    npc = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def health_percentage(self):
        return (self.health / self.max_health) * 100


class Backpack(models.Model):
    owner = models.OneToOneField(Character, on_delete=models.CASCADE)

    def __str__(self):
        return self.owner.name


class Weapon(models.Model):
    name = models.CharField(max_length=50)
    icon = models.ImageField(blank=True, upload_to="uploads/")
    damage = models.IntegerField()
    type = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    backpack = models.ForeignKey(Backpack, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


class Armor(models.Model):
    name = models.CharField(max_length=50)
    icon = models.ImageField(blank=True, upload_to="uploads/")
    defense = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)
    backpack = models.ForeignKey(Backpack, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name
