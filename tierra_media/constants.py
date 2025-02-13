from .models import Faction, Location, Race

def npc_init():
    NPCS = [
        {
            "name": "Aragorn",
            "max_health": 250,
            "health": 250,
            "defense": 50,
            "faction": Faction.objects.get(name__iexact="la comunidad del anillo"),
            "location": Location.objects.get(name__iexact="minas tirith"),
            "race": Race.objects.get(name__iexact="humano"),
            "npc": True,
        },
        {
            "name": "Legolas",
            "max_health": 250,
            "health": 250,
            "defense": 50,
            "faction": Faction.objects.get(name__iexact="lothlorien"),
            "location": Location.objects.get(name__iexact="bosque negro"),
            "race": Race.objects.get(name__iexact="elfo"),
            "npc": True,
        },
        {
            "name": "Gimli",
            "max_health": 250,
            "health": 250,
            "defense": 50,
            "faction": Faction.objects.get(name__iexact="la comunidad del anillo"),
            "location": Location.objects.get(name__iexact="lothlorien"),
            "race": Race.objects.get(name__iexact="enano"),
            "npc": True,
        },
        {
            "name": "Frodo",
            "max_health": 250,
            "health": 250,
            "defense": 50,
            "faction": Faction.objects.get(name__iexact="la comunidad del anillo"),
            "location": Location.objects.get(name__iexact="hobbiton"),
            "race": Race.objects.get(name__iexact="hobbit"),
            "npc": True,
        },
        {
            "name": "Boromir",
            "max_health": 250,
            "health": 250,
            "defense": 50,
            "faction": Faction.objects.get(name__iexact="rivendel"),
            "location": Location.objects.get(name__iexact="rivendel"),
            "race": Race.objects.get(name__iexact="humano"),
            "npc": True,
        },
        {
            "name": "Saruman",
            "max_health": 250,
            "health": 250,
            "defense": 50,
            "faction": Faction.objects.get(name__iexact="isengard"),
            "location": Location.objects.get(name__iexact="isengard"),
            "race": Race.objects.get(name__iexact="humano"),
            "npc": True,
        },
        {
            "name": "Sauron",
            "max_health": 250,
            "health": 250,
            "defense": 50,
            "faction": Faction.objects.get(name__iexact="mordor"),
            "location": Location.objects.get(name__iexact="mordor"),
            "race": Race.objects.get(name__iexact="humano"),
            "npc": True,
        },
        {
            "name": "Lurtz",
            "max_health": 250,
            "health": 250,
            "defense": 50,
            "faction": Faction.objects.get(name__iexact="mordor"),
            "location": Location.objects.get(name__iexact="mordor"),
            "race": Race.objects.get(name__iexact="orco"),
            "npc": True,
        },
    ]

    return NPCS

def common_weapons_init():
    WEAPONS = [
        {
            "name": "Glamdring",
            "damage": 15,
            "type": "sword"
        },
        {
            "name": "Narsail",
            "damage": 15,
            "type": "sword"
        },
        {
            "name": "Nymera",
            "damage": 15,
            "type": "bow"
        },
        {
            "name": "Liora",
            "damage": 15,
            "type": "bow"
        },
        {
            "name": "Keldorn",
            "damage": 15,
            "type": "mace"
        },
        {
            "name": "Vorak",
            "damage": 15,
            "type": "mace"
        },
        {
            "name": "Astrid",
            "damage": 15,
            "type": "axe"
        },
        {
            "name": "Zharok",
            "damage": 15,
            "type": "axe"
        },
    ]