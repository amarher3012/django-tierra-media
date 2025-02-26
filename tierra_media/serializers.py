from rest_framework import serializers
from .models import Character, Weapon, Armor, Location, Faction, Race


class WeaponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weapon
        fields = ["name", "damage", "type"]


class ArmorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Armor
        fields = ["name", "defense"]


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["name"]


class FactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faction
        fields = ["name"]


class RaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Race
        fields = ["name"]


class CharacterSerializer(serializers.ModelSerializer):
    equipped_weapon = WeaponSerializer(read_only=True)
    equipped_armor = ArmorSerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    faction = FactionSerializer(read_only=True)
    race = RaceSerializer(read_only=True)

    class Meta:
        model = Character
        fields = [
            "id",
            "name",
            "sex",
            "health",
            "max_health",
            "defense",
            "equipped_weapon",
            "equipped_armor",
            "faction",
            "location",
            "race",
        ]
