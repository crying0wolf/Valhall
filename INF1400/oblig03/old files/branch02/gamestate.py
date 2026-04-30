"""Enum for alle skjerm- og spilltilstander.

Tilstandene brukes i hovedløkken for å avgjøre hva som skal tegnes og
hvilken input som skal være aktiv.
"""

from enum import Enum, auto

class GameState(Enum):
    SPLASH = auto()
    MAIN_MENU = auto()
    LOAD_MENU = auto()
    GAME_OVER = auto()
    INTRO_SEQUENCE = auto()
    CHARACTER_SELECT = auto()
    CHARACTER_BRIEFING = auto()
    STARTER_SELECT = auto()
    MAIN_GAME = auto()
    OPTIONS = auto()
    INFO = auto()
    GYM = auto()
    SHOP = auto()
    ITEMS = auto()
    PARTY = auto()