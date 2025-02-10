from django.db import models
from django.contrib.auth.models import User


class Faction(models.Model):
    name = models.CharField(unique=True, max_length=50)

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(unique=True, max_length=50)

    def __str__(self):
        return self.name


class Race(models.Model):
    name = models.CharField(unique=True, max_length=50)

    def __str__(self):
        return self.name


class Character(models.Model):
    name = models.CharField(max_length=50)
    max_health = models.IntegerField(default=250)
    health = models.IntegerField(default=250)
    defense = models.IntegerField(default=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    faction = models.ForeignKey(Faction, on_delete=models.DO_NOTHING)
    location = models.ForeignKey(Location, on_delete=models.DO_NOTHING)
    race = models.ForeignKey(Race, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.name


class NPC(models.Model):
    name = models.CharField(max_length=50)
    max_health = models.IntegerField(default=250)
    health = models.IntegerField(default=250)
    defense = models.IntegerField(default=50)
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    faction = models.ForeignKey(Faction, on_delete=models.DO_NOTHING)
    location = models.ForeignKey(Location, on_delete=models.DO_NOTHING)
    race = models.ForeignKey(Race, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.name


class Relationship(models.Model):
    type = models.CharField(max_length=50)
    character_1 = models.ForeignKey(
        Character, related_name="character", on_delete=models.CASCADE
    )
    character_2 = models.ForeignKey(
        Character, related_name="relation_with", on_delete=models.CASCADE
    )

    def __str__(self):
        return (
            self.character_1.name + " -> " + self.character_2.name + " -> " + self.type
        )


class Weapon(models.Model):
    name = models.CharField(unique=True, max_length=50)
    damage = models.IntegerField()
    type = models.CharField(max_length=50)
    owner = models.ManyToManyField(Character)
    npc_owned = models.BooleanField()

    def __str__(self):
        return self.name


class Armor(models.Model):
    name = models.CharField(unique=True, max_length=50)
    defense = models.IntegerField()
    owner = models.ManyToManyField(Character)

    def __str__(self):
        return self.name
