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
            "max_health": 250,
            "health": 250,
            "defense": 50,
            "faction": "La Comunidad del Anillo",
            "location": "Minas Tirith",
            "race": "Humano",
            "npc": True,
        },
        {
            "name": "Legolas",
            "max_health": 250,
            "health": 250,
            "defense": 50,
            "faction": "Lothlorien",
            "location": "Bosque Negro",
            "race": "Elfo",
            "npc": True,
        },
        {
            "name": "Gimli",
            "max_health": 250,
            "health": 250,
            "defense": 50,
            "faction": "La Comunidad del Anillo",
            "location": "Lothlorien",
            "race": "Enano",
            "npc": True,
        },
        {
            "name": "Frodo",
            "max_health": 250,
            "health": 250,
            "defense": 50,
            "faction": "La Comunidad del Anillo",
            "location": "Hobbiton",
            "race": "Hobbit",
            "npc": True,
        },
        {
            "name": "Boromir",
            "max_health": 250,
            "health": 250,
            "defense": 50,
            "faction": "Rivendel",
            "location": "Rivendel",
            "race": "Humano",
            "npc": True,
        },
        {
            "name": "Saruman",
            "max_health": 250,
            "health": 250,
            "defense": 50,
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
            "max_health": 250,
            "health": 250,
            "defense": 50,
            "faction": "Mordor",
            "location": "Mordor",
            "race": "Orco",
            "npc": True,
        },
    ]

    return NPCS

def weapons_init():
    weapons = [
        {
            "name": "Aelion",
            "damage": 10,
            "type": "sword",
        },
        {
            "name": "Balathor",
            "damage": 10,
            "type": "sword",
        },
        {
            "name": "Thalion",
            "damage": 10,
            "type": "bow",
        },
        {
            "name": "Eledrin",
            "damage": 10,
            "type": "bow",
        },
        {
            "name": "Faelion",
            "damage": 10,
            "type": "mace",
        },
        {
            "name": "Amdir",
            "damage": 10,
            "type": "mace",
        },
    ]

    return weapons

def armors_init():
    armors = [
        {
            "name": "Thalionir",
            "defense": 10,
            "type": "helmet",
        },
        {
            "name": "Gorundor",
            "defense": 10,
            "type": "helmet",
        },
        {
            "name": "Eldrinel",
            "defense": 10,
            "type": "chest",
        },
        {
            "name": "Kaelorn",
            "defense": 10,
            "type": "chest",
        },
        {
            "name": "Faethor",
            "defense": 10,
            "type": "gloves",
        },
        {
            "name": "Ithilwen",
            "defense": 10,
            "type": "gloves",
        },
    ]

    return armors