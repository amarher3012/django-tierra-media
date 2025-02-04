from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Faction(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Race(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Character(models.Model):
    name = models.CharField(unique=True, max_length=50)
    max_health = models.IntegerField()
    health = models.IntegerField()
    defense = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    faction = models.ForeignKey(Faction, on_delete=models.DO_NOTHING)
    location = models.ForeignKey(Location, on_delete=models.DO_NOTHING)
    race = models.ForeignKey(Race, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.name


class Relationship(models.Model):
    type = models.CharField(max_length=50)
    character = models.OneToOneField(Character, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.character.name}: {self.type}"


class Backpack(models.Model):
    character = models.OneToOneField(Character, on_delete=models.CASCADE)

    def __str__(self):
        return self.character.name


class Weapon(models.Model):
    name = models.CharField(unique=True, max_length=50)
    damage = models.IntegerField()
    type = models.CharField(max_length=50)
    equipment = models.ForeignKey(Backpack, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Armor(models.Model):
    name = models.CharField(unique=True, max_length=50)
    defense = models.IntegerField()
    equipment = models.ForeignKey(Backpack, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
