SEX = ["M", "F"]

SEX_CHOICES = [(SEX[0], "Hombre"), (SEX[1], "Mujer")]

FACTIONS = [
    "La Comunidad del Anillo",
    "Lothlorien",
    "Rivendel",
    "Mordor",
    "Isengard",
]

FACTION_CHOICES = [
    (FACTIONS[0], FACTIONS[0]),
    (FACTIONS[1], FACTIONS[1]),
    (FACTIONS[2], FACTIONS[2]),
    (FACTIONS[3], FACTIONS[3]),
    (FACTIONS[4], FACTIONS[4]),
]

LOCATIONS = [
    "Minas Tirith",
    "Bosque Negro",
    "Lothlorien",
    "Hobbiton",
    "Rivendel",
    "Isengard",
    "Mordor",
]

LOCATION_CHOICES = [
    (LOCATIONS[0], LOCATIONS[0]),
    (LOCATIONS[1], LOCATIONS[1]),
    (LOCATIONS[2], LOCATIONS[2]),
    (LOCATIONS[3], LOCATIONS[3]),
    (LOCATIONS[4], LOCATIONS[4]),
    (LOCATIONS[5], LOCATIONS[5]),
    (LOCATIONS[6], LOCATIONS[6]),
]

RACES = [
    "Humano",
    "Elfo",
    "Enano",
    "Hobbit",
    "Orco",
]

RACE_CHOICES = [
    (RACES[0], RACES[0]),
    (RACES[1], RACES[1]),
    (RACES[2], RACES[2]),
    (RACES[3], RACES[3]),
    (RACES[4], RACES[4]),
]


def npc_init():
    NPCS = [
        {
            "name": "Aragorn",
            "max_health": 200,
            "health": 200,
            "defense": 30,
            "faction": "La Comunidad del Anillo",
            "location": "Minas Tirith",
            "race": "Humano",
            "npc": True,
        },
        {
            "name": "Legolas",
            "max_health": 180,
            "health": 180,
            "defense": 20,
            "faction": "Lothlorien",
            "location": "Bosque Negro",
            "race": "Elfo",
            "npc": True,
        },
        {
            "name": "Gimli",
            "max_health": 220,
            "health": 220,
            "defense": 40,
            "faction": "La Comunidad del Anillo",
            "location": "Lothlorien",
            "race": "Enano",
            "npc": True,
        },
        {
            "name": "Frodo",
            "max_health": 125,
            "health": 125,
            "defense": 15,
            "faction": "La Comunidad del Anillo",
            "location": "Hobbiton",
            "race": "Hobbit",
            "npc": True,
        },
        {
            "name": "Boromir",
            "max_health": 180,
            "health": 180,
            "defense": 30,
            "faction": "Rivendel",
            "location": "Rivendel",
            "race": "Humano",
            "npc": True,
        },
        {
            "name": "Saruman",
            "max_health": 180,
            "health": 180,
            "defense": 25,
            "faction": "Isengard",
            "location": "Isengard",
            "race": "Humano",
            "npc": True,
        },
        {
            "name": "Sauron",
            "max_health": 250,
            "health": 250,
            "defense": 50,
            "faction": "Mordor",
            "location": "Mordor",
            "race": "Orco",
            "npc": True,
        },
        {
            "name": "Lurtz",
            "max_health": 230,
            "health": 230,
            "defense": 40,
            "faction": "Mordor",
            "location": "Mordor",
            "race": "Orco",
            "npc": True,
        },
    ]

    return NPCS


def weapons_init():
    weapons = [
        {"name": "Andrath", "damage": 9, "type": "sword"},
        {"name": "Caladhril", "damage": 7, "type": "sword"},
        {"name": "Elenarth", "damage": 10, "type": "sword"},
        {"name": "Gildorim", "damage": 6, "type": "sword"},
        {"name": "Morglad", "damage": 8, "type": "sword"},

        {"name": "Nimloth", "damage": 5, "type": "bow"},
        {"name": "Oronion", "damage": 9, "type": "bow"},
        {"name": "Thrandor", "damage": 6, "type": "bow"},
        {"name": "Vaerion", "damage": 7, "type": "bow"},
        {"name": "Eärendur", "damage": 10, "type": "bow"},

        {"name": "Barazûl", "damage": 8, "type": "axe"},
        {"name": "Drâkhmar", "damage": 4, "type": "axe"},
        {"name": "Gurthang", "damage": 9, "type": "axe"},
        {"name": "Kazrâd", "damage": 7, "type": "axe"},
        {"name": "Zirakthul", "damage": 6, "type": "axe"},

        {"name": "Amonir", "damage": 10, "type": "mace"},
        {"name": "Durthar", "damage": 5, "type": "mace"},
        {"name": "Felagûnd", "damage": 8, "type": "mace"},
        {"name": "Lómendur", "damage": 7, "type": "mace"},
        {"name": "Tharûl", "damage": 9, "type": "mace"},
    ]

    return weapons


def armors_init():
    armors = [
        {"name": "Aerendil", "defense": 4},
        {"name": "Calenmir", "defense": 10},
        {"name": "Dorhael", "defense": 6},
        {"name": "Elarion", "defense": 9},
        {"name": "Galadhrim", "defense": 5},
        {"name": "Halethor", "defense": 7},
        {"name": "Isilvar", "defense": 8},
        {"name": "Lorindor", "defense": 6},
        {"name": "Menelthor", "defense": 9},
        {"name": "Nimrond", "defense": 4},
        {"name": "Orophir", "defense": 10},
        {"name": "Silmaril", "defense": 7},
        {"name": "Vaelion", "defense": 8},
    ]

    return armors
