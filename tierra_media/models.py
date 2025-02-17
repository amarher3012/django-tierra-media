from django.db import models
from django.contrib.auth.models import User
from .constants import FACTION_CHOICES, LOCATION_CHOICES, RACE_CHOICES


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
    icon = models.ImageField(blank=True, upload_to="uploads/character-icons/")
    name = models.CharField(max_length=50)
    max_health = models.IntegerField(default=250)
    health = models.IntegerField(default=250)
    defense = models.IntegerField(default=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    faction = models.ForeignKey(Faction, on_delete=models.DO_NOTHING)
    location = models.ForeignKey(Location, on_delete=models.DO_NOTHING)
    race = models.ForeignKey(Race, on_delete=models.DO_NOTHING)
    npc = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Weapon(models.Model):
    icon = models.ImageField(blank=True, upload_to="uploads/weapon-icons/")
    name = models.CharField(unique=True, max_length=50)
    damage = models.IntegerField()
    type = models.CharField(max_length=50)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class UniqueWeapon(Weapon):
    owner = models.OneToOneField(Character, on_delete=models.CASCADE)


class CommonWeapon(Weapon):
    owner = models.ManyToManyField(Character)


class Armor(models.Model):
    icon = models.ImageField(blank=True, upload_to="uploads/armor-icons/")
    name = models.CharField(unique=True, max_length=50)
    defense = models.IntegerField()
    type = models.CharField(max_length=50)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class UniqueArmor(Armor):
    owner = models.OneToOneField(Character, on_delete=models.CASCADE)


class CommonArmor(Armor):
    owner = models.ManyToManyField(Character)
