"""Grunndata for arter, typer og typeeffektivitet.

Denne modulen beskriver hvilke Pokemon-arter som finnes i spillet og
hvilke grunnverdier de starter med.
"""

from enum import Enum, auto
import random

class PokemonType(Enum):
    NORMAL = auto()
    LIGHTNING = auto()
    FIRE = auto()
    WATER = auto()
    GHOST = auto()
    ICE = auto()
    FLYING = auto()
    GRASS = auto()
    DRAGON = auto()

class Species(Enum):
    EEVEE = auto()
    PIKACHU = auto()
    JOLTEON = auto()
    RAICHU = auto()
    FLAREON = auto()
    CHARMANDER = auto()
    CHARMELEON = auto()
    CHARIZARD = auto()
    MOLTRES = auto()
    VULPIX = auto()
    NINETALES = auto()
    SQUIRTLE = auto()
    WARTORTLE = auto()
    BLASTOISE = auto()
    STARYU = auto()
    STARMIE = auto()
    VAPOREON = auto()
    GASTLY = auto()
    HAUNTER = auto()
    GENGAR = auto()
    PIDGEY = auto()
    PIDGEOTTO = auto()
    PIDGEOT = auto()
    BULBASAUR = auto()
    IVYSAUR = auto()
    VENUSAUR = auto()
    DRATINI = auto()
    DRAGONAIR = auto()


TYPE_EFFECTIVENESS: dict[PokemonType, dict[PokemonType, float]] = {
    PokemonType.FIRE: {
        PokemonType.GRASS: 2.0,
        PokemonType.ICE: 2.0,
        PokemonType.WATER: 0.5,
        PokemonType.FIRE: 0.5,
        PokemonType.DRAGON: 0.5,
    },
    PokemonType.WATER: {
        PokemonType.FIRE: 2.0,
        PokemonType.WATER: 0.5,
        PokemonType.GRASS: 0.5,
        PokemonType.DRAGON: 0.5,
    },
    PokemonType.GRASS: {
        PokemonType.WATER: 2.0,
        PokemonType.FIRE: 0.5,
        PokemonType.GRASS: 0.5,
        PokemonType.FLYING: 0.5,
        PokemonType.DRAGON: 0.5,
    },
    PokemonType.LIGHTNING: {
        PokemonType.WATER: 2.0,
        PokemonType.FLYING: 2.0,
        PokemonType.GRASS: 0.5,
        PokemonType.DRAGON: 0.5,
        PokemonType.LIGHTNING: 0.5,
    },
    PokemonType.ICE: {
        PokemonType.GRASS: 2.0,
        PokemonType.FLYING: 2.0,
        PokemonType.DRAGON: 2.0,
        PokemonType.FIRE: 0.5,
        PokemonType.WATER: 0.5,
        PokemonType.ICE: 0.5,
    },
    PokemonType.FLYING: {
        PokemonType.GRASS: 2.0,
        PokemonType.LIGHTNING: 0.5,
    },
    PokemonType.GHOST: {
        PokemonType.GHOST: 2.0,
        PokemonType.NORMAL: 0.0,
    },
    PokemonType.NORMAL: {
        PokemonType.GHOST: 0.0,
    },
    PokemonType.DRAGON: {
        PokemonType.DRAGON: 2.0,
    },
}


def get_type_multiplier(attacker_type: PokemonType, defender_type: PokemonType) -> float:
    return TYPE_EFFECTIVENESS.get(attacker_type, {}).get(defender_type, 1.0)


def get_effectiveness_text(multiplier: float) -> str:
    if multiplier == 0.0:
        return "It had no effect."
    if multiplier > 1.0:
        return "It's super effective!"
    if multiplier < 1.0:
        return "It's not very effective."
    return ""


# Oppslagsverk for artens grunndata. Disse verdiene brukes når en Pokemon lages.
POKEMON_DATA = {
                Species.PIDGEOTTO: {
                    "type": PokemonType.FLYING,
                    "base_hp": 63,
                    "base_attack": 60,
                    "base_defense": 55,
                    "base_speed": 71,
                    "base_evade": 7,
                    "base_agility": 10,
                },
                Species.PIDGEOT: {
                    "type": PokemonType.FLYING,
                    "base_hp": 83,
                    "base_attack": 80,
                    "base_defense": 75,
                    "base_speed": 101,
                    "base_evade": 8,
                    "base_agility": 12,
                },
                Species.STARYU: {
                    "type": PokemonType.WATER,
                    "base_hp": 30,
                    "base_attack": 45,
                    "base_defense": 55,
                    "base_speed": 85,
                    "base_evade": 7,
                    "base_agility": 10,
                },
                Species.VAPOREON: {
                    "type": PokemonType.WATER,
                    "base_hp": 130,
                    "base_attack": 65,
                    "base_defense": 60,
                    "base_speed": 65,
                    "base_evade": 7,
                    "base_agility": 10,
                },
                Species.GASTLY: {
                    "type": PokemonType.GHOST,
                    "base_hp": 30,
                    "base_attack": 35,
                    "base_defense": 30,
                    "base_speed": 80,
                    "base_evade": 8,
                    "base_agility": 12,
                },
                Species.GENGAR: {
                    "type": PokemonType.GHOST,
                    "base_hp": 60,
                    "base_attack": 65,
                    "base_defense": 60,
                    "base_speed": 110,
                    "base_evade": 9,
                    "base_agility": 14,
                },
                Species.MOLTRES: {
                    "type": PokemonType.FIRE,
                    "base_hp": 90,
                    "base_attack": 100,
                    "base_defense": 90,
                    "base_speed": 90,
                    "base_evade": 10,
                    "base_agility": 15,
                },
                Species.DRATINI: {
                    "type": PokemonType.DRAGON,
                    "base_hp": 41,
                    "base_attack": 64,
                    "base_defense": 45,
                    "base_speed": 50,
                    "base_evade": 6,
                    "base_agility": 8,
                },
                Species.EEVEE: {
                    "type": PokemonType.NORMAL,
                    "base_hp": 55,
                    "base_attack": 55,
                    "base_defense": 50,
                    "base_speed": 55,
                    "base_evade": 6,
                    "base_agility": 8,
                },
            Species.PIDGEY: {
                "type": PokemonType.FLYING,
                "base_hp": 40,
                "base_attack": 45,
                "base_defense": 40,
                "base_speed": 56,
                "base_evade": 6,
                "base_agility": 8,
            },
        Species.VULPIX: {
            "type": PokemonType.FIRE,
            "base_hp": 38,
            "base_attack": 41,
            "base_defense": 40,
            "base_speed": 65,
            "base_evade": 7,
            "base_agility": 10,
        },
    Species.EEVEE: {
        "type": PokemonType.NORMAL,
        "base_hp": 50,
        "base_attack": 8,
        "base_defense": 8,
        "base_speed": 10,
        "base_evade": 5,
        "base_agility": 7,
    },
    Species.PIKACHU: {
        "type": PokemonType.LIGHTNING,
        "base_hp": 45,
        "base_attack": 50,
        "base_defense": 8,
        "base_speed": 14,
        "base_evade": 6,
        "base_agility": 10,
    },
    # ...fill in others similarly
    Species.JOLTEON: {
        "type": PokemonType.LIGHTNING,
        "base_hp": 65,
        "base_attack": 110,
        "base_defense": 60,
        "base_speed": 130,
        "base_evade": 8,
        "base_agility": 12,
    },
    Species.SQUIRTLE: {
        "type": PokemonType.WATER,
        "base_hp": 44,
        "base_attack": 48,
        "base_defense": 65,
        "base_speed": 43,
        "base_evade": 5,
        "base_agility": 7,
    },
    Species.BULBASAUR: {
        "type": PokemonType.GRASS,
        "base_hp": 45,
        "base_attack": 49,
        "base_defense": 49,
        "base_speed": 45,
    },
    Species.IVYSAUR: {
        "type": PokemonType.GRASS,
        "base_hp": 60,
        "base_attack": 62,
        "base_defense": 63,
        "base_speed": 60,
    },
    Species.VENUSAUR: {
        "type": PokemonType.GRASS,
        "base_hp": 80,
        "base_attack": 82,
        "base_defense": 83,
        "base_speed": 80,
    },
    Species.CHARMANDER: {
        "type": PokemonType.FIRE,
        "base_hp": 39,
        "base_attack": 52,
        "base_defense": 43,
        "base_speed": 65,
    },
    Species.CHARMELEON: {
        "type": PokemonType.FIRE,
        "base_hp": 58,
        "base_attack": 64,
        "base_defense": 58,
        "base_speed": 80,
    },
    Species.CHARIZARD: {
        "type": PokemonType.FIRE,
        "base_hp": 78,
        "base_attack": 84,
        "base_defense": 78,
        "base_speed": 100,
    },
    Species.RAICHU: {
        "type": PokemonType.LIGHTNING,
        "base_hp": 60,
        "base_attack": 90,
        "base_defense": 55,
        "base_speed": 110,
        "base_evade": 8,
        "base_agility": 12,
    },
    Species.FLAREON: {
        "type": PokemonType.FIRE,
        "base_hp": 65,
        "base_attack": 130,
        "base_defense": 60,
        "base_speed": 65,
        "base_evade": 7,
        "base_agility": 10,
    },
    Species.NINETALES: {
        "type": PokemonType.FIRE,
        "base_hp": 73,
        "base_attack": 76,
        "base_defense": 75,
        "base_speed": 100,
        "base_evade": 8,
        "base_agility": 12,
    },
    Species.WARTORTLE: {
        "type": PokemonType.WATER,
        "base_hp": 59,
        "base_attack": 63,
        "base_defense": 80,
        "base_speed": 58,
        "base_evade": 6,
        "base_agility": 8,
    },
    Species.BLASTOISE: {
        "type": PokemonType.WATER,
        "base_hp": 79,
        "base_attack": 83,
        "base_defense": 100,
        "base_speed": 78,
        "base_evade": 7,
        "base_agility": 10,
    },
    Species.STARMIE: {
        "type": PokemonType.WATER,
        "base_hp": 60,
        "base_attack": 75,
        "base_defense": 85,
        "base_speed": 115,
        "base_evade": 8,
        "base_agility": 12,
    },
    Species.HAUNTER: {
        "type": PokemonType.GHOST,
        "base_hp": 45,
        "base_attack": 50,
        "base_defense": 45,
        "base_speed": 95,
        "base_evade": 8,
        "base_agility": 12,
    },
    Species.DRAGONAIR: {
        "type": PokemonType.DRAGON,
        "base_hp": 61,
        "base_attack": 84,
        "base_defense": 65,
        "base_speed": 70,
        "base_evade": 7,
        "base_agility": 10,
    },
}