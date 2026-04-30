"""Hovedfil for Pokemon Care Simulator.

Filen samler oppstart av Pygame, lasting av ressurser, hjelpelogikk for
lyd og menyer, samt hovedløkken som styrer input, oppdatering og tegning.
Kommentarene under er ment som en kort norsk guide til de viktigste delene.
"""

import math
import os
import random
import sys
from datetime import datetime
from time import time

import pygame

from data import POKEMON_DATA, Species
from gamestate import GameState
from player import Player
from pokemon import Pokemon
from save_manager import SaveManager
from sprite_manager import SpriteManager
from ui import Button, PokeballButton, draw_health_bar, draw_text, set_mouse_position_provider
from world import World


# Konstanter og filstier brukes på tvers av hele spillet.
SCREEN_WIDTH = 880
SCREEN_HEIGHT = 660
DISPLAY_SCALE_OPTIONS = [1.0, 1.25, 1.5, 1.75]
FARM_MIN_X = 18
FARM_MAX_X = 526
FARM_MIN_Y = 92
FARM_MAX_Y = 500
POTION_COST = 200
REVIVE_COST = 500
CURE_COST = 300
AUTO_SAVE_INTERVAL = 300
BASE_DIR = os.path.dirname(__file__)
SPRITES_DIR = os.path.join(BASE_DIR, "sprites")
CHARACTERS_DIR = os.path.join(BASE_DIR, "characters")
MANUAL_SAVE_FILES = [
    os.path.join(BASE_DIR, "manual_save_1.json"),
    os.path.join(BASE_DIR, "manual_save_2.json"),
    os.path.join(BASE_DIR, "manual_save_3.json"),
]
MANUAL_SAVE_FILE = MANUAL_SAVE_FILES[0]
AUTOSAVE_FILE = os.path.join(BASE_DIR, "autosave.json")
OPENING_MUSIC_DIR = os.path.join(BASE_DIR, "sound", "music", "opening")
FARM_MUSIC_DIR = os.path.join(BASE_DIR, "sound", "music", "farm")
BATTLE_MUSIC_DIR = os.path.join(BASE_DIR, "sound", "music", "battle")
GYM_MUSIC_DIR = os.path.join(BASE_DIR, "sound", "music", "gym")
SHOP_MUSIC_DIR = os.path.join(BASE_DIR, "sound", "music", "shop")
SFX_DIR = os.path.join(BASE_DIR, "sound", "sfx")
BATTLE_BG_PATH = os.path.join(BASE_DIR, "bg", "battle.png")
FARM_BG_PATH = os.path.join(BASE_DIR, "bg", "farm.png")
SHOP_BG_PATH = os.path.join(BASE_DIR, "bg", "shop.png")
MAIN_MENU_BG_PATH = os.path.join(BASE_DIR, "bg", "mainmenu.png")
UIT_LOGO_PATH = os.path.join(BASE_DIR, "bg", "uit_logo.png")
OPENING_MUSIC_FILES = [
    os.path.join(OPENING_MUSIC_DIR, "remakeopening01.ogg"),
    os.path.join(OPENING_MUSIC_DIR, "remakeopening02.ogg"),
    os.path.join(OPENING_MUSIC_DIR, "remakeopening03.ogg"),
]
STARTUP_SPLASH_FADE_IN = 1.85
STARTUP_SPLASH_HOLD = 11.55
STARTUP_SPLASH_FADE_OUT = 1.1
FARM_MUSIC_FILES = [
    os.path.join(FARM_MUSIC_DIR, "Pixel Hearts Reloaded.ogg"),
    os.path.join(FARM_MUSIC_DIR, "Pixel Hearts Reloaded (1).ogg"),
]
BATTLE_MUSIC_FILES = [
    os.path.join(BATTLE_MUSIC_DIR, "battleVSwildPokémon01.ogg"),
    os.path.join(BATTLE_MUSIC_DIR, "battleVSwildPokémon02.ogg"),
    os.path.join(BATTLE_MUSIC_DIR, "battleVSwildPokémon03.ogg"),
    os.path.join(BATTLE_MUSIC_DIR, "battleVSwildPokémon04.ogg"),
]
GYM_MUSIC_FILES = [
    os.path.join(GYM_MUSIC_DIR, "gym_battle_loop_01.wav"),
    os.path.join(GYM_MUSIC_DIR, "gym_battle_loop_02.wav"),
]
SHOP_MUSIC_FILES = [
    os.path.join(SHOP_MUSIC_DIR, "soft_shop_loop_01.wav"),
    os.path.join(SHOP_MUSIC_DIR, "soft_shop_loop_02.wav"),
    os.path.join(SHOP_MUSIC_DIR, "soft_shop_loop_03.wav"),
]
SFX_PATHS = {
    "hover": os.path.join(SFX_DIR, "hover.wav"),
    "click": os.path.join(SFX_DIR, "click.wav"),
    "intro_transition": os.path.join(SFX_DIR, "intro_transition.wav"),
    "buy": os.path.join(SFX_DIR, "buy.wav"),
    "item_used": os.path.join(SFX_DIR, "item_used.wav"),
    "attack": os.path.join(SFX_DIR, "attack.wav"),
    "hit": os.path.join(SFX_DIR, "hit.wav"),
    "catch": os.path.join(SFX_DIR, "catch.wav"),
    "bounce": os.path.join(SFX_DIR, "bounce.wav"),
    "leader_entrance": os.path.join(SFX_DIR, "leader_entrance.wav"),
    "menu_reverb": os.path.join(SFX_DIR, "menu_reverb.wav"),
    "alert": os.path.join(SFX_DIR, "alert.wav"),
}
CHARACTER_FRONT_ASSET_FILES = {
    "Henrik": "henrik_front.png",
    "Anna": "anne_front.png",
    "Martin": "martin_front.png",
}
CHARACTER_BACK_ASSET_FILES = {
    "Henrik": "henrik_back.png",
    "Anna": "anne_back.png",
    "Martin": "martin_back.png",
}
GYM_LEADER_NAME = "Jonas"
GYM_LEADER_FRONT_ASSET_FILE = "jonas_front.png"
GYM_LEADER_BACK_ASSET_FILE = "jonas_back.png"
GYM_OPPONENT_TEAMS = {
    "Henrik": Species.CHARIZARD,
    "Anna": Species.VAPOREON,
    "Martin": Species.GENGAR,
}
GYM_RECOMMENDED_LEVELS = [10, 15]
GYM_LEADER_RECOMMENDED_LEVEL = 20
GYM_BADGE_STYLES = {
    "Henrik": {"fill": (226, 108, 74), "border": (255, 212, 142), "shape": "sun"},
    "Anna": {"fill": (72, 152, 230), "border": (186, 236, 255), "shape": "drop"},
    "Martin": {"fill": (144, 94, 214), "border": (228, 206, 255), "shape": "diamond"},
    GYM_LEADER_NAME: {"fill": (214, 182, 64), "border": (255, 244, 180), "shape": "crown"},
}
GYM_DIALOGUE = {
    "Henrik": "You made it this far. Show me your fire.",
    "Anna": "Let's see if your team can handle real pressure.",
    "Martin": "Stay sharp. One mistake and the match is mine.",
    GYM_LEADER_NAME: "Two badges earned. Now prove you belong at the top.",
}
GYM_LEADER_SPECIES = Species.MOLTRES
INTRO_DIALOGUE_TEXT = "Hello?! Who are you?.."

SPRITE_PATHS = {
    Species.PIKACHU: os.path.join(SPRITES_DIR, "pikachu.png"),
    Species.RAICHU: os.path.join(SPRITES_DIR, "raichu.png"),
    Species.CHARMANDER: os.path.join(SPRITES_DIR, "charmander.png"),
    Species.SQUIRTLE: os.path.join(SPRITES_DIR, "squirtle.png"),
    Species.WARTORTLE: os.path.join(SPRITES_DIR, "wartortle.png"),
    Species.BLASTOISE: os.path.join(SPRITES_DIR, "blastoise.png"),
    Species.EEVEE: os.path.join(SPRITES_DIR, "eevee.png"),
    Species.JOLTEON: os.path.join(SPRITES_DIR, "jolteon.png"),
    Species.FLAREON: os.path.join(SPRITES_DIR, "flareon.png"),
    Species.MOLTRES: os.path.join(SPRITES_DIR, "moltres.png"),
    Species.VULPIX: os.path.join(SPRITES_DIR, "vulpix.png"),
    Species.NINETALES: os.path.join(SPRITES_DIR, "ninetales.png"),
    Species.STARYU: os.path.join(SPRITES_DIR, "staryu.png"),
    Species.STARMIE: os.path.join(SPRITES_DIR, "starmie.png"),
    Species.VAPOREON: os.path.join(SPRITES_DIR, "vaporeon.png"),
    Species.GASTLY: os.path.join(SPRITES_DIR, "gastly.png"),
    Species.HAUNTER: os.path.join(SPRITES_DIR, "haunter.png"),
    Species.GENGAR: os.path.join(SPRITES_DIR, "gengar.png"),
    Species.PIDGEY: os.path.join(SPRITES_DIR, "pidgey.png"),
    Species.PIDGEOTTO: os.path.join(SPRITES_DIR, "pidgeotto.png"),
    Species.PIDGEOT: os.path.join(SPRITES_DIR, "pidgeot.png"),
    Species.BULBASAUR: os.path.join(SPRITES_DIR, "bulbasaur.png"),
    Species.IVYSAUR: os.path.join(SPRITES_DIR, "ivysaur.png"),
    Species.VENUSAUR: os.path.join(SPRITES_DIR, "venusaur.png"),
    Species.DRATINI: os.path.join(SPRITES_DIR, "dratini.png"),
    Species.DRAGONAIR: os.path.join(SPRITES_DIR, "dragonair.png"),
    Species.CHARMELEON: os.path.join(SPRITES_DIR, "charmeleon.png"),
    Species.CHARIZARD: os.path.join(SPRITES_DIR, "charizard.png"),
}


# Start Pygame én gang og opprett objekter som brukes i hele kjøretiden.
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()
if pygame.mixer.get_init() != (44100, -16, 2):
    if pygame.mixer.get_init() is not None:
        pygame.mixer.quit()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
pygame.mixer.set_num_channels(12)
display_scale_index = 0


def current_display_scale() -> float:
    return DISPLAY_SCALE_OPTIONS[display_scale_index]


def create_window_for_scale(scale: float) -> pygame.Surface:
    scaled_size = (max(1, int(SCREEN_WIDTH * scale)), max(1, int(SCREEN_HEIGHT * scale)))
    return pygame.display.set_mode(scaled_size)


window = create_window_for_scale(current_display_scale())
screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)).convert()
pygame.display.set_caption("Pokémon Care Simulator")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)
small_font = pygame.font.SysFont(None, 22)
tiny_font = pygame.font.SysFont(None, 20)
title_font = pygame.font.SysFont(None, 48)

# Last alle sprites tidlig, slik at tegnefunksjonene kan hente dem uten å lese fra disk senere.
sprite_manager = SpriteManager()
for species, path in SPRITE_PATHS.items():
    sprite_manager.load(species, path)
    sprite_manager.load_battle_set(species, SPRITES_DIR)

# Lydeffekter er valgfrie ved oppstart. Manglende filer ignoreres i stedet for å krasje spillet.
sfx: dict[str, pygame.mixer.Sound] = {}
for effect_name, effect_path in SFX_PATHS.items():
    if os.path.exists(effect_path):
        sfx[effect_name] = pygame.mixer.Sound(effect_path)

ambient_channel = pygame.mixer.Channel(1)

# Bakgrunner får en enkel reserveflate hvis bildefilen mangler.
if os.path.exists(BATTLE_BG_PATH):
    battle_background = pygame.image.load(BATTLE_BG_PATH).convert()
    battle_background = pygame.transform.scale(battle_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
else:
    battle_background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    battle_background.fill((52, 80, 96))

if os.path.exists(FARM_BG_PATH):
    farm_background = pygame.image.load(FARM_BG_PATH).convert()
    farm_background = pygame.transform.scale(farm_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
else:
    farm_background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    farm_background.fill((72, 120, 72))

if os.path.exists(SHOP_BG_PATH):
    shop_background = pygame.image.load(SHOP_BG_PATH).convert()
    shop_background = pygame.transform.scale(shop_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
else:
    shop_background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    shop_background.fill((32, 28, 24))

if os.path.exists(MAIN_MENU_BG_PATH):
    main_menu_background = pygame.image.load(MAIN_MENU_BG_PATH).convert()
    main_menu_background = pygame.transform.scale(main_menu_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
else:
    main_menu_background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    main_menu_background.fill((22, 24, 42))

if os.path.exists(UIT_LOGO_PATH):
    startup_logo = pygame.image.load(UIT_LOGO_PATH).convert_alpha()
    alpha_bounds = startup_logo.get_bounding_rect(min_alpha=1)
    if alpha_bounds.width > 0 and alpha_bounds.height > 0:
        startup_logo = startup_logo.subsurface(alpha_bounds).copy()
    logo_width, logo_height = startup_logo.get_size()
    scale_ratio = min((SCREEN_WIDTH * 0.72) / max(1, logo_width), (SCREEN_HEIGHT * 0.46) / max(1, logo_height))
    startup_logo = pygame.transform.smoothscale(
        startup_logo,
        (max(1, int(logo_width * scale_ratio)), max(1, int(logo_height * scale_ratio))),
    )
else:
    startup_logo = None


# Alle knapper opprettes én gang og gjenbrukes i hovedløkken.
menu_button_color = (176, 136, 44)
menu_text_color = (44, 28, 8)
menu_start_btn = Button(356, 198, 168, 42, "New Game", font, menu_button_color, menu_text_color)
menu_load_btn = Button(356, 256, 168, 42, "Load File", font, menu_button_color, menu_text_color)
menu_options_btn = Button(356, 314, 168, 42, "Options", font, menu_button_color, menu_text_color)
menu_exit_btn = Button(356, 372, 168, 42, "Exit", font, menu_button_color, menu_text_color)
load_autosave_btn = Button(320, 200, 240, 42, "Autosave", font, menu_button_color, menu_text_color)
load_slot_1_btn = Button(320, 258, 240, 42, "Manual Save 1", font, menu_button_color, menu_text_color)
load_slot_2_btn = Button(320, 316, 240, 42, "Manual Save 2", font, menu_button_color, menu_text_color)
load_slot_3_btn = Button(320, 374, 240, 42, "Manual Save 3", font, menu_button_color, menu_text_color)
load_back_btn = Button(320, 440, 240, 42, "Back", font, menu_button_color, menu_text_color)
game_over_continue_btn = Button(320, 360, 240, 46, "Continue", font, menu_button_color, menu_text_color)
game_over_quit_btn = Button(320, 422, 240, 46, "Quit to Main Menu", font, menu_button_color, menu_text_color)

options_back_btn = Button(365, 542, 150, 42, "Back", font)
options_main_menu_btn = Button(314, 486, 108, 34, "Quit", small_font, (132, 48, 48), (255, 236, 236))
sound_vol_down_btn = Button(420, 176, 40, 40, "-", font)
sound_vol_up_btn = Button(580, 176, 40, 40, "+", font)
sound_mute_btn = Button(640, 176, 100, 40, "Mute", font)
music_vol_down_btn = Button(420, 246, 40, 40, "-", font)
music_vol_up_btn = Button(580, 246, 40, 40, "+", font)
music_mute_btn = Button(640, 246, 100, 40, "Mute", font)
resolution_scale_btn = Button(600, 310, 150, 36, "Scale: 100%", small_font)

pikachu_btn = Button(160, 320, 150, 50, "Pikachu", font)
charmander_btn = Button(365, 320, 150, 50, "Charmander", font)
squirtle_btn = Button(570, 320, 150, 50, "Squirtle", font)
henrik_character_btn = Button(112, 288, 192, 228, "Henrik", font)
anna_character_btn = Button(344, 288, 192, 228, "Anna", font)
martin_character_btn = Button(576, 288, 192, 228, "Martin", font)
briefing_accept_btn = Button(360, 518, 160, 44, "Accept", font)

feed_button = Button(692, 202, 144, 32, "Feed", small_font, (112, 86, 44))
pet_button = Button(692, 240, 144, 32, "Pet", small_font, (98, 64, 122))
sleep_button = Button(692, 278, 144, 32, "Sleep", small_font, (56, 88, 136))
walk_button = Button(276, 532, 248, 42, "Trip", font, (54, 112, 90))
gym_button = Button(700, 346, 112, 30, "PokeGym", small_font)
attack_button = Button(626, 390, 112, 30, "Attack", small_font)
catch_button = Button(626, 426, 112, 30, "Catch", small_font)
shop_button = Button(698, 462, 112, 30, "Shop", small_font)
save_button = Button(610, 522, 128, 34, "Save", font)
load_button = Button(610, 562, 128, 28, "Load", font)
items_button = Button(618, 462, 112, 30, "Items", small_font)

shop_potion_btn = Button(250, 190, 300, 55, "Potion - $200", font)
shop_revive_btn = Button(250, 270, 300, 55, "Revive Medicine - $500", font)
shop_cure_btn = Button(250, 350, 300, 55, "Cure - $300", font)
shop_back_btn = Button(325, 455, 150, 50, "Back", font)

items_potion_btn = Button(250, 190, 300, 55, "Use Potion", font)
items_revive_btn = Button(250, 270, 300, 55, "Use Revive Medicine", font)
items_cure_btn = Button(250, 350, 300, 55, "Use Cure", font)
items_back_btn = Button(325, 455, 150, 50, "Back", font)

party_button = PokeballButton(780, 406, 30, "", font)
options_button = Button(756, 568, 88, 24, "Options", tiny_font)
info_button = Button(722, 114, 78, 26, "Info", tiny_font)
options_save_btn = Button(300, 388, 120, 40, "Save", small_font)
options_load_btn = Button(460, 388, 120, 40, "Load", small_font)
low_effects_toggle_btn = Button(370, 440, 140, 36, "Low Effects: On", small_font)
cheats_toggle_btn = Button(442, 486, 130, 36, "Cheats: Off", small_font)
level_up_button = Button(20, 356, 200, 32, "Level Up", font)
evolve_button = Button(20, 394, 200, 32, "Evolve", font)
party_item_btn_width = 70
party_item_btn_height = 22
party_item_start_x = 494
party_item_start_y = 480
party_set_active_btn = Button(party_item_start_x, party_item_start_y - party_item_btn_height - 16, party_item_btn_width + 40, party_item_btn_height, "Set Active", tiny_font, (120, 120, 60))
party_potion_btn = Button(party_item_start_x, party_item_start_y, party_item_btn_width, party_item_btn_height, "Potion", tiny_font, (92, 76, 46))
party_revive_btn = Button(party_item_start_x, party_item_start_y + party_item_btn_height + 8, party_item_btn_width, party_item_btn_height, "Revive", tiny_font, (92, 54, 54))
party_cure_btn = Button(party_item_start_x, party_item_start_y + 2 * (party_item_btn_height + 8), party_item_btn_width, party_item_btn_height, "Cure", tiny_font, (54, 96, 82))
party_scroll_up_btn = Button(370, 190, 58, 24, "Up", tiny_font)
party_scroll_down_btn = Button(370, 456, 58, 24, "Down", tiny_font)
party_back_btn = Button(220, 560, 150, 50, "Back", font)
info_back_btn = Button(325, 530, 150, 46, "Back", font)
gym_back_btn = Button(325, 518, 150, 46, "Back", font)


screen_shake_timer = 0.0
screen_shake_offset = [0, 0]
sound_volume = 5
music_volume = 5
sound_muted = False
music_muted = False
low_effects_enabled = True
potions = 0
state = GameState.SPLASH
player: Player | None = None
world: World | None = None
running = True
last_time = time()
last_auto_save = time()
opening_music_playing = False
current_opening_track = ""
current_music_mode = ""
current_music_track = ""
music_cycle_indices = {
    "shop": 0,
}
music_shuffle_bags: dict[str, list[str]] = {}
last_music_track_by_mode: dict[str, str] = {}
pending_music_request: tuple[str, list[str], bool, int] | None = None
music_transition_deadline = 0.0
options_return_state = GameState.MAIN_MENU
load_menu_return_state = GameState.MAIN_MENU
cheats_enabled = False
status_message = "Welcome to the farm."
status_message_timer = 3.0
status_message_queue: list[tuple[str, float]] = []
game_over_message = "All your Pokémon are in the hospital."
game_over_title = "Game Over"
game_over_is_victory = False
game_over_auto_return_timer = 0.0
game_over_fade_alpha = 0.0
hovered_button_text = ""
farm_actor_state: dict[int, dict[str, float | bool]] = {}
main_menu_fade_alpha = 255.0
startup_splash_timer = 0.0
startup_splash_sound_played = False
selected_farm_pokemon: Pokemon | None = None
selected_party_pokemon: Pokemon | None = None
party_scroll_offset = 0
dragged_farm_pokemon: Pokemon | None = None
drag_offset = (0.0, 0.0)
drag_motion_samples: list[tuple[float, float, float]] = []
last_bounce_sound_time = 0.0
danger_alert_ids: set[int] = set()
danger_started_at: dict[int, float] = {}
last_danger_alert_time = 0.0
character_portraits: dict[str, pygame.Surface] = {}
character_back_portraits: dict[str, pygame.Surface] = {}
pending_player_character: str | None = None
intro_phase = "idle"
intro_phase_timer = 0.0
intro_overlay_alpha = 0.0
starter_select_fade_alpha = 0.0
briefing_page_index = 0
music_track_cache: dict[tuple[str, ...], list[str]] = {}
last_applied_music_volume: float | None = None
farm_side_panel_surface: pygame.Surface | None = None
farm_portrait_cache: dict[str, tuple[pygame.Surface, pygame.Surface]] = {}
surface_transform_cache: dict[tuple[int, int, int, bool, bool], pygame.Surface] = {}
filled_surface_cache: dict[tuple[int, int, tuple[int, int, int, int]], pygame.Surface] = {}


def apply_music_settings():
    """Juster faktisk musikkvolum ut fra modus og spillerens innstillinger."""
    global last_applied_music_volume

    base_level = 0.0 if music_muted else (music_volume / 10) * 0.42
    if state in {GameState.OPTIONS, GameState.ITEMS}:
        base_level *= 0.7
    if current_music_mode == "farm":
        music_level = base_level * 0.26
    elif current_music_mode == "battle":
        music_level = base_level * 0.72
    elif current_music_mode == "gym":
        music_level = base_level * 0.6
    elif current_music_mode == "shop":
        music_level = base_level * 0.18
    else:
        music_level = base_level * 0.82
    if last_applied_music_volume is not None and abs(last_applied_music_volume - music_level) < 0.0001:
        return
    pygame.mixer.music.set_volume(music_level)
    last_applied_music_volume = music_level


def present_frame():
    if window.get_size() == (SCREEN_WIDTH, SCREEN_HEIGHT):
        window.blit(screen, (0, 0))
    else:
        scaled_frame = pygame.transform.smoothscale(screen, window.get_size())
        window.blit(scaled_frame, (0, 0))
    pygame.display.flip()


def to_logical_pos(position: tuple[int, int]) -> tuple[int, int]:
    window_width, window_height = window.get_size()
    if window_width == SCREEN_WIDTH and window_height == SCREEN_HEIGHT:
        return position

    logical_x = int(position[0] * SCREEN_WIDTH / max(1, window_width))
    logical_y = int(position[1] * SCREEN_HEIGHT / max(1, window_height))
    logical_x = max(0, min(SCREEN_WIDTH - 1, logical_x))
    logical_y = max(0, min(SCREEN_HEIGHT - 1, logical_y))
    return logical_x, logical_y


def get_mouse_pos() -> tuple[int, int]:
    return to_logical_pos(pygame.mouse.get_pos())


def normalize_mouse_event(event: pygame.event.Event) -> pygame.event.Event:
    if event.type not in {pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP}:
        return event

    event_data = event.dict.copy()
    if "pos" in event_data:
        event_data["pos"] = to_logical_pos(event_data["pos"])
    if "rel" in event_data:
        window_width, window_height = window.get_size()
        event_data["rel"] = (
            int(event_data["rel"][0] * SCREEN_WIDTH / max(1, window_width)),
            int(event_data["rel"][1] * SCREEN_HEIGHT / max(1, window_height)),
        )
    return pygame.event.Event(event.type, event_data)


def cycle_display_scale():
    global display_scale_index, window

    display_scale_index = (display_scale_index + 1) % len(DISPLAY_SCALE_OPTIONS)
    window = create_window_for_scale(current_display_scale())
    pygame.display.set_caption("Pokémon Care Simulator")
    set_status_message(f"Resolution scale set to {int(current_display_scale() * 100)}%.", duration=2.2)


set_mouse_position_provider(get_mouse_pos)


def available_tracks(track_list: list[str]) -> list[str]:
    cache_key = tuple(track_list)
    cached_tracks = music_track_cache.get(cache_key)
    if cached_tracks is not None:
        return cached_tracks

    existing_tracks = [track for track in track_list if os.path.exists(track)]
    music_track_cache[cache_key] = existing_tracks
    return existing_tracks


def play_sound(effect_name: str, volume_scale: float = 1.0):
    """Spill en enkel lydeffekt hvis lyd er aktivert og filen ble lastet inn."""
    if sound_muted:
        return

    sound = sfx.get(effect_name)
    if sound is None:
        return

    sound.set_volume(min(1.0, (sound_volume / 10) * max(0.0, volume_scale)))
    sound.play()


def play_startup_logo_sound():
    if "menu_reverb" in sfx:
        play_sound("menu_reverb", volume_scale=0.52)
    else:
        play_sound("intro_transition", volume_scale=0.4)


def next_music_track(mode: str, tracks: list[str], randomize: bool) -> str:
    if randomize:
        bag = [track for track in music_shuffle_bags.get(mode, []) if track in tracks]
        if not bag:
            bag = list(tracks)
            random.shuffle(bag)
            last_track = last_music_track_by_mode.get(mode, "")
            if len(bag) > 1 and bag[0] == last_track:
                bag.append(bag.pop(0))
        track = bag.pop(0)
        music_shuffle_bags[mode] = bag
        last_music_track_by_mode[mode] = track
        return track

    next_index = music_cycle_indices.get(mode, 0) % len(tracks)
    music_cycle_indices[mode] = (next_index + 1) % len(tracks)
    return tracks[next_index]


def start_music_playback(mode: str, track_list: list[str], randomize: bool = True, fade_ms: int = 800):
    global current_music_mode, current_music_track, opening_music_playing, current_opening_track

    tracks = available_tracks(track_list)
    if not tracks:
        return

    track = next_music_track(mode, tracks, randomize)
    apply_music_settings()
    pygame.mixer.music.load(track)
    pygame.mixer.music.play(0, fade_ms=fade_ms)

    current_music_mode = mode
    current_music_track = track
    opening_music_playing = mode == "opening"
    if mode == "opening":
        current_opening_track = track


def update_music_transition():
    global pending_music_request, music_transition_deadline

    if pending_music_request is None or time() < music_transition_deadline:
        return

    mode, track_list, randomize, fade_ms = pending_music_request
    pending_music_request = None
    music_transition_deadline = 0.0
    start_music_playback(mode, track_list, randomize, fade_ms)


def play_music(mode: str, track_list: list[str], randomize: bool = True, fade_ms: int = 800, force: bool = False):
    global pending_music_request, music_transition_deadline

    tracks = available_tracks(track_list)
    if not tracks:
        return

    if pending_music_request is not None:
        pending_mode, _, _, _ = pending_music_request
        if pending_mode == mode and not force:
            return

    if not force and current_music_mode == mode and pygame.mixer.music.get_busy():
        apply_music_settings()
        return

    if pygame.mixer.music.get_busy() and current_music_mode != mode:
        pending_music_request = (mode, track_list, randomize, fade_ms)
        music_transition_deadline = time() + min(fade_ms, 450) / 1000
        pygame.mixer.music.fadeout(min(fade_ms, 450))
        return

    start_music_playback(mode, track_list, randomize, fade_ms)


def show_options_menu(return_state: GameState):
    global state, options_return_state

    options_return_state = return_state
    state = GameState.OPTIONS


def show_load_menu(return_state: GameState):
    global state, load_menu_return_state

    load_menu_return_state = return_state
    state = GameState.LOAD_MENU


def resolve_save_file(filename: str) -> str:
    return filename


def save_slot_exists(filename: str) -> bool:
    return os.path.exists(resolve_save_file(filename))


def latest_save_file() -> str | None:
    candidates: list[tuple[float, str]] = []
    seen_paths: set[str] = set()
    for filename in [AUTOSAVE_FILE, *MANUAL_SAVE_FILES]:
        resolved = resolve_save_file(filename)
        if resolved in seen_paths or not os.path.exists(resolved):
            continue
        seen_paths.add(resolved)
        candidates.append((os.path.getmtime(resolved), filename))

    if not candidates:
        return None

    candidates.sort(key=lambda entry: entry[0], reverse=True)
    return candidates[0][1]


def save_slot_name(filename: str) -> str:
    if filename == AUTOSAVE_FILE:
        return "Autosave"
    if filename == MANUAL_SAVE_FILES[0]:
        return "Manual Save 1"
    if filename == MANUAL_SAVE_FILES[1]:
        return "Manual Save 2"
    if filename == MANUAL_SAVE_FILES[2]:
        return "Manual Save 3"
    return "Save File"


def save_timestamp_label(filename: str | None) -> str:
    if filename is None:
        return "Last saved: No save file found"

    resolved = resolve_save_file(filename)
    if not os.path.exists(resolved):
        return "Last saved: No save file found"

    saved_at = datetime.fromtimestamp(os.path.getmtime(resolved)).strftime("%Y-%m-%d %H:%M:%S")
    return f"Last saved: {saved_at}"


def slot_button_label(base_label: str, filename: str) -> str:
    suffix = "Ready" if save_slot_exists(filename) else "Empty"
    return f"{base_label} - {suffix}"


def show_info_menu():
    global state

    state = GameState.INFO


def return_to_main_menu():
    global state, main_menu_fade_alpha, selected_farm_pokemon, game_over_auto_return_timer, game_over_fade_alpha, game_over_is_victory, game_over_title

    state = GameState.MAIN_MENU
    main_menu_fade_alpha = 255.0
    selected_farm_pokemon = None
    game_over_title = "Game Over"
    game_over_is_victory = False
    game_over_auto_return_timer = 0.0
    game_over_fade_alpha = 0.0
    reset_new_game_intro()


def show_game_over_screen(message: str | None = None, title: str = "Game Over", is_victory: bool = False, auto_return_delay: float = 0.0):
    global state, game_over_message, game_over_title, game_over_is_victory, game_over_auto_return_timer, game_over_fade_alpha, selected_farm_pokemon, dragged_farm_pokemon, drag_motion_samples

    if message is not None:
        game_over_message = message
    game_over_title = title
    game_over_is_victory = is_victory
    game_over_auto_return_timer = max(0.0, auto_return_delay)
    game_over_fade_alpha = 0.0
    selected_farm_pokemon = None
    dragged_farm_pokemon = None
    drag_motion_samples = []
    state = GameState.GAME_OVER


def continue_from_latest_save() -> bool:
    latest_file = latest_save_file()
    if latest_file is None:
        set_status_message("No autosave or manual save is available.")
        return False
    return load_game(latest_file)


def update_hover_sound(buttons: list[Button]):
    global hovered_button_text

    mouse_pos = get_mouse_pos()
    hovered_button = next((button for button in buttons if button.rect.collidepoint(mouse_pos)), None)
    hovered_text = hovered_button.text if hovered_button else ""
    if hovered_text != hovered_button_text:
        if hovered_text:
            play_sound("hover")
        hovered_button_text = hovered_text


def click_button(button: Button, event: pygame.event.Event) -> bool:
    if button.is_clicked(event):
        play_sound("click")
        return True
    return False


def play_random_opening_music():
    play_music("opening", OPENING_MUSIC_FILES, randomize=True)


def play_farm_music(force: bool = False):
    play_music("farm", FARM_MUSIC_FILES, randomize=True, fade_ms=1100, force=force)


def play_battle_music(force: bool = False):
    play_music("battle", BATTLE_MUSIC_FILES, randomize=True, fade_ms=1200, force=force)


def play_gym_music(force: bool = False):
    play_music("gym", GYM_MUSIC_FILES, randomize=True, fade_ms=1350, force=force)


def play_shop_music(force: bool = False):
    play_music("shop", SHOP_MUSIC_FILES, randomize=False, fade_ms=1300, force=force)


def update_menu_reverb():
    reverb_sound = sfx.get("menu_reverb")
    if reverb_sound is None:
        return

    should_play = state in {GameState.OPTIONS, GameState.ITEMS}
    if should_play:
        ambient_channel.set_volume(0.0 if music_muted else (music_volume / 10) * 0.14)
        if not ambient_channel.get_busy():
            ambient_channel.play(reverb_sound, loops=-1)
    elif ambient_channel.get_busy():
        ambient_channel.fadeout(260)


def fade_out_opening_music():
    global opening_music_playing, current_music_mode, current_music_track, pending_music_request, music_transition_deadline

    if not opening_music_playing:
        return

    pygame.mixer.music.fadeout(1200)


def finish_startup_splash():
    global state, main_menu_fade_alpha, startup_splash_timer, startup_splash_sound_played, startup_splash_timer

    state = GameState.MAIN_MENU
    main_menu_fade_alpha = 255.0
    startup_splash_timer = 0.0
    startup_splash_sound_played = False
    play_random_opening_music()


def update_startup_splash(delta: float):
    global startup_splash_sound_played, startup_splash_timer

    if state != GameState.SPLASH:
        return

    startup_splash_timer += delta
    if not startup_splash_sound_played and startup_splash_timer >= 0.16:
        play_startup_logo_sound()
        startup_splash_sound_played = True

    total_duration = STARTUP_SPLASH_FADE_IN + STARTUP_SPLASH_HOLD + STARTUP_SPLASH_FADE_OUT
    if startup_splash_timer >= total_duration:
        finish_startup_splash()


def scale_surface_to_fit(surface: pygame.Surface, max_width: int, max_height: int) -> pygame.Surface:
    width, height = surface.get_size()
    if width == 0 or height == 0:
        return pygame.Surface((max_width, max_height), pygame.SRCALPHA)

    ratio = min(max_width / width, max_height / height)
    scaled_size = (max(1, int(width * ratio)), max(1, int(height * ratio)))
    return pygame.transform.smoothscale(surface, scaled_size)


def get_cached_transformed_surface(
    surface: pygame.Surface,
    width: int,
    height: int,
    *,
    smooth: bool = False,
    flip_horizontal: bool = False,
) -> pygame.Surface:
    cache_key = (id(surface), width, height, smooth, flip_horizontal)
    cached_surface = surface_transform_cache.get(cache_key)
    if cached_surface is not None:
        return cached_surface

    transform_fn = pygame.transform.smoothscale if smooth else pygame.transform.scale
    transformed_surface = transform_fn(surface, (width, height))
    if flip_horizontal:
        transformed_surface = pygame.transform.flip(transformed_surface, True, False)
    surface_transform_cache[cache_key] = transformed_surface
    return transformed_surface


def get_cached_filled_surface(width: int, height: int, color: tuple[int, int, int, int]) -> pygame.Surface:
    cache_key = (width, height, color)
    if cache_key in filled_surface_cache:
        return filled_surface_cache[cache_key]

    filled_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    filled_surface.fill(color)
    filled_surface_cache[cache_key] = filled_surface
    return filled_surface


def get_farm_side_panel_surface() -> pygame.Surface:
    global farm_side_panel_surface

    if farm_side_panel_surface is None:
        farm_side_panel_surface = pygame.Surface((210, SCREEN_HEIGHT), pygame.SRCALPHA)
        farm_side_panel_surface.fill((18, 24, 36, 220))
    return farm_side_panel_surface


def get_cached_farm_portrait(trainer_name: str) -> tuple[pygame.Surface, pygame.Surface]:
    cached_visuals = farm_portrait_cache.get(trainer_name)
    if cached_visuals is not None:
        return cached_visuals

    trainer_portrait = character_portraits.get(trainer_name, create_character_placeholder(trainer_name, 132, 160))
    scaled_trainer_portrait = pygame.transform.smoothscale(
        trainer_portrait,
        (int(trainer_portrait.get_width() * 1.24), int(trainer_portrait.get_height() * 1.24)),
    )
    portrait_shadow = pygame.Surface((scaled_trainer_portrait.get_width() + 28, scaled_trainer_portrait.get_height() + 18), pygame.SRCALPHA)
    pygame.draw.ellipse(
        portrait_shadow,
        (0, 0, 0, 120),
        pygame.Rect(18, scaled_trainer_portrait.get_height() - 8, scaled_trainer_portrait.get_width() - 28, 18),
    )
    farm_portrait_cache[trainer_name] = (scaled_trainer_portrait, portrait_shadow)
    return farm_portrait_cache[trainer_name]


def create_character_placeholder(name: str, width: int = 132, height: int = 160) -> pygame.Surface:
    placeholder = pygame.Surface((width, height), pygame.SRCALPHA)
    placeholder.fill((34, 48, 82))
    pygame.draw.rect(placeholder, (110, 168, 255), placeholder.get_rect(), width=3, border_radius=18)
    center_x = width // 2
    pygame.draw.circle(placeholder, (86, 118, 170), (center_x, int(height * 0.35)), max(18, width // 5))
    pygame.draw.circle(placeholder, (70, 96, 145), (center_x, int(height * 0.74)), max(28, width // 3))
    label = tiny_font.render(name[0], True, (232, 242, 255))
    label_rect = label.get_rect(center=(center_x, int(height * 0.35)))
    placeholder.blit(label, label_rect)
    return placeholder


def load_character_portraits(asset_map: dict[str, str], max_width: int, max_height: int) -> dict[str, pygame.Surface]:
    portraits: dict[str, pygame.Surface] = {}
    for name, filename in asset_map.items():
        portrait_path = os.path.join(CHARACTERS_DIR, filename)
        if os.path.exists(portrait_path):
            portrait = pygame.image.load(portrait_path).convert_alpha()
            portraits[name] = scale_surface_to_fit(portrait, max_width, max_height)
        else:
            portraits[name] = create_character_placeholder(name, max_width, max_height)
    return portraits


def load_extra_character_portrait(name: str, filename: str, max_width: int, max_height: int) -> pygame.Surface:
    portrait_path = os.path.join(CHARACTERS_DIR, filename)
    if os.path.exists(portrait_path):
        portrait = pygame.image.load(portrait_path).convert_alpha()
        return scale_surface_to_fit(portrait, max_width, max_height)
    return create_character_placeholder(name, max_width, max_height)


def reset_new_game_intro(clear_character: bool = True):
    global briefing_page_index, hovered_button_text, intro_overlay_alpha, intro_phase, intro_phase_timer, pending_player_character, starter_select_fade_alpha

    hovered_button_text = ""
    intro_overlay_alpha = 0.0
    intro_phase = "idle"
    intro_phase_timer = 0.0
    starter_select_fade_alpha = 0.0
    briefing_page_index = 0
    if clear_character:
        pending_player_character = None


def start_new_game_intro():
    global intro_overlay_alpha, intro_phase, intro_phase_timer, pending_player_character, state, starter_select_fade_alpha

    pending_player_character = None
    intro_phase = "menu_fade"
    intro_phase_timer = 0.0
    intro_overlay_alpha = 0.0
    starter_select_fade_alpha = 0.0
    state = GameState.INTRO_SEQUENCE


def show_character_select():
    global hovered_button_text, intro_overlay_alpha, intro_phase, intro_phase_timer, state

    hovered_button_text = ""
    intro_phase = "selection_delay"
    intro_phase_timer = 0.0
    intro_overlay_alpha = 0.0
    state = GameState.CHARACTER_SELECT


def show_character_briefing():
    global briefing_page_index, intro_overlay_alpha, intro_phase, intro_phase_timer, state

    intro_phase = "briefing_reveal"
    intro_phase_timer = 0.0
    intro_overlay_alpha = 255.0
    briefing_page_index = 0
    state = GameState.CHARACTER_BRIEFING


def advance_intro_flow(delta: float):
    global intro_overlay_alpha, intro_phase, intro_phase_timer, starter_select_fade_alpha, state

    if state == GameState.INTRO_SEQUENCE:
        intro_phase_timer += delta
        if intro_phase == "menu_fade":
            intro_overlay_alpha = min(255.0, intro_overlay_alpha + 420 * delta)
            if intro_overlay_alpha >= 255.0:
                intro_phase = "dialogue_reveal"
                intro_phase_timer = 0.0
                play_sound("intro_transition")
        elif intro_phase == "dialogue_reveal":
            intro_overlay_alpha = max(0.0, intro_overlay_alpha - 220 * delta)
            if intro_phase_timer >= 0.9 and intro_overlay_alpha <= 0:
                intro_phase = "await_continue"
                intro_phase_timer = 0.0

    elif state == GameState.CHARACTER_SELECT:
        intro_phase_timer += delta
        if intro_phase == "selection_delay" and intro_phase_timer >= 0.7:
            intro_phase = "selection_ready"
            intro_phase_timer = 0.0
        elif intro_phase == "selection_fade":
            intro_overlay_alpha = min(255.0, intro_overlay_alpha + 360 * delta)
            if intro_overlay_alpha >= 255.0:
                show_character_briefing()

    elif state == GameState.CHARACTER_BRIEFING:
        intro_phase_timer += delta
        if intro_phase == "briefing_reveal":
            intro_overlay_alpha = max(0.0, intro_overlay_alpha - 220 * delta)
            if intro_overlay_alpha <= 0:
                intro_phase = "briefing_ready"
                intro_phase_timer = 0.0
        elif intro_phase == "briefing_fade":
            intro_overlay_alpha = min(255.0, intro_overlay_alpha + 320 * delta)
            if intro_overlay_alpha >= 255.0:
                state = GameState.STARTER_SELECT
                starter_select_fade_alpha = 255.0
                intro_phase = "idle"
                intro_phase_timer = 0.0
                intro_overlay_alpha = 0.0

    elif state == GameState.STARTER_SELECT and starter_select_fade_alpha > 0:
        starter_select_fade_alpha = max(0.0, starter_select_fade_alpha - 220 * delta)


def wrap_text_lines(text: str, text_font: pygame.font.Font, max_width: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]

    lines = [words[0]]
    for word in words[1:]:
        candidate = f"{lines[-1]} {word}"
        if text_font.size(candidate)[0] <= max_width:
            lines[-1] = candidate
        else:
            lines.append(word)
    return lines


def draw_dialogue_bubble(text: str, prompt: str | None = None):
    bubble_rect = pygame.Rect(104, 132, 592, 146)
    shadow = pygame.Surface((bubble_rect.width + 12, bubble_rect.height + 12), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, 90), shadow.get_rect(), border_radius=24)
    screen.blit(shadow, (bubble_rect.x + 6, bubble_rect.y + 8))
    pygame.draw.rect(screen, (44, 94, 192), bubble_rect, border_radius=22)
    pygame.draw.rect(screen, (170, 214, 255), bubble_rect, width=3, border_radius=22)
    pygame.draw.circle(screen, (44, 94, 192), (140, bubble_rect.bottom + 10), 18)
    pygame.draw.circle(screen, (170, 214, 255), (140, bubble_rect.bottom + 10), 18, width=3)

    draw_text(screen, "???", 136, 150, small_font, (216, 236, 255))
    for index, line in enumerate(wrap_text_lines(text, title_font, 500)):
        draw_text(screen, line, 136, 182 + index * 38, title_font, (250, 250, 255))

    if prompt:
        prompt_color = (226, 238, 255) if (pygame.time.get_ticks() // 350) % 2 == 0 else (166, 194, 240)
        draw_text(screen, prompt, 136, 240, tiny_font, prompt_color)


def draw_character_card(button: Button, portrait: pygame.Surface, is_hovered: bool, is_ready: bool):
    card_rect = button.rect
    shadow = pygame.Surface((card_rect.width + 14, card_rect.height + 14), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, 90), shadow.get_rect(), border_radius=22)
    screen.blit(shadow, (card_rect.x + 6, card_rect.y + 8))

    panel_color = (22, 38, 78) if is_ready else (18, 30, 58)
    border_color = (118, 202, 255) if is_hovered and is_ready else (80, 122, 190)
    pygame.draw.rect(screen, panel_color, card_rect, border_radius=20)
    pygame.draw.rect(screen, border_color, card_rect, width=3, border_radius=20)

    portrait_frame = pygame.Rect(card_rect.x + 22, card_rect.y + 20, card_rect.width - 44, 164)
    pygame.draw.rect(screen, (12, 20, 42), portrait_frame, border_radius=16)

    portrait_to_draw = portrait
    if is_hovered and is_ready:
        glow = pygame.Surface((portrait_frame.width + 18, portrait_frame.height + 18), pygame.SRCALPHA)
        pygame.draw.rect(glow, (88, 196, 255, 46), glow.get_rect(), border_radius=20)
        screen.blit(glow, (portrait_frame.x - 9, portrait_frame.y - 9), special_flags=pygame.BLEND_RGBA_ADD)
        portrait_to_draw = pygame.transform.smoothscale(
            portrait,
            (int(portrait.get_width() * 1.04), int(portrait.get_height() * 1.04)),
        )

    portrait_rect = portrait_to_draw.get_rect(center=portrait_frame.center)
    screen.blit(portrait_to_draw, portrait_rect)

    if not is_hovered:
        mute_overlay = pygame.Surface(portrait_frame.size, pygame.SRCALPHA)
        mute_overlay.fill((24, 34, 64, 88))
        screen.blit(mute_overlay, portrait_frame.topleft)

    if not is_ready:
        lock_overlay = pygame.Surface(card_rect.size, pygame.SRCALPHA)
        lock_overlay.fill((8, 14, 26, 92))
        screen.blit(lock_overlay, card_rect.topleft)

    name_color = (248, 250, 255) if is_ready else (200, 210, 225)
    name_surface = font.render(button.text, True, name_color)
    name_rect = name_surface.get_rect(center=(card_rect.centerx, card_rect.y + 196))
    screen.blit(name_surface, name_rect)

    subtitle = "Ready" if is_ready else "Hold on..."
    subtitle_surface = tiny_font.render(subtitle, True, (160, 214, 255))
    subtitle_rect = subtitle_surface.get_rect(center=(card_rect.centerx, card_rect.y + 218))
    screen.blit(subtitle_surface, subtitle_rect)


def get_other_character_names(selected_name: str) -> list[str]:
    return [name for name in CHARACTER_FRONT_ASSET_FILES if name != selected_name]


def get_briefing_lines(selected_name: str) -> list[tuple[str, str]]:
    other_names = get_other_character_names(selected_name)
    if len(other_names) < 2:
        return []

    return [
        (other_names[0], f"{selected_name}, the farm needs you now."),
        (other_names[1], "We can only afford to give you one Pokemon to start with."),
        (other_names[0], f"But you are all right? You can catch them all, right, {selected_name}?"),
        (other_names[1], "Save the farm and gather all the Pokemon you can."),
    ]


def draw_briefing_character(name: str, portrait: pygame.Surface, x: int):
    frame_rect = pygame.Rect(x, 150, 200, 268)
    pygame.draw.rect(screen, (18, 28, 54), frame_rect, border_radius=22)
    pygame.draw.rect(screen, (112, 184, 255), frame_rect, width=3, border_radius=22)
    portrait_rect = portrait.get_rect(center=(frame_rect.centerx, frame_rect.y + 126))
    screen.blit(portrait, portrait_rect)
    name_surface = font.render(name, True, (240, 246, 255))
    name_rect = name_surface.get_rect(center=(frame_rect.centerx, frame_rect.bottom - 30))
    screen.blit(name_surface, name_rect)


def draw_briefing_dialogue(selected_name: str):
    lines = get_briefing_lines(selected_name)
    if not lines:
        return

    current_page = min(briefing_page_index, len(lines) - 1)
    speaker, line = lines[current_page]

    bubble_rect = pygame.Rect(112, 372, 576, 132)
    pygame.draw.rect(screen, (16, 30, 62), bubble_rect, border_radius=24)
    pygame.draw.rect(screen, (146, 206, 255), bubble_rect, width=3, border_radius=24)

    speaker_surface = small_font.render(f"{speaker}:", True, (190, 224, 255))
    speaker_rect = speaker_surface.get_rect(topleft=(142, 394))
    screen.blit(speaker_surface, speaker_rect)

    wrapped_lines = wrap_text_lines(line, font, 420)
    for index, wrapped_line in enumerate(wrapped_lines):
        text_surface = font.render(wrapped_line, True, (245, 248, 255))
        screen.blit(text_surface, (142, 426 + index * 28))

    page_text = f"{current_page + 1}/{len(lines)}"
    draw_text(screen, page_text, 620, 388, tiny_font, (182, 208, 245))

    if current_page < len(lines) - 1:
        draw_text(screen, "Click Next to continue", 142, 476, tiny_font, (194, 216, 245))
        briefing_accept_btn.text = "Next"
    else:
        draw_text(screen, "Press Accept to begin choosing your starter.", 142, 476, tiny_font, (194, 216, 245))
        briefing_accept_btn.text = "Accept"


def draw_battle_info_box(title: str, value: str, x: int, y: int, width: int = 230):
    panel = get_cached_filled_surface(width, 54, (8, 12, 24, 158))
    screen.blit(panel, (x, y))
    draw_text(screen, title, x + 12, y + 8, tiny_font, (182, 210, 255))
    draw_text(screen, value, x + 12, y + 26, small_font, (245, 246, 250))


def draw_pokeball(screen_surface: pygame.Surface, center_x: int, center_y: int, radius: int = 16):
    outline_color = (24, 24, 30)
    pygame.draw.circle(screen_surface, outline_color, (center_x, center_y), radius + 2)
    pygame.draw.circle(screen_surface, (242, 242, 242), (center_x, center_y), radius)
    pygame.draw.circle(screen_surface, (216, 64, 64), (center_x, center_y), radius)
    pygame.draw.rect(screen_surface, (242, 242, 242), (center_x - radius, center_y, radius * 2, radius))
    pygame.draw.line(screen_surface, outline_color, (center_x - radius + 2, center_y), (center_x + radius - 2, center_y), 4)
    pygame.draw.circle(screen_surface, outline_color, (center_x, center_y), max(5, radius // 3 + 3))
    pygame.draw.circle(screen_surface, (245, 245, 245), (center_x, center_y), max(4, radius // 3))


def draw_catch_animation(encounter):
    if not getattr(encounter, "catch_anim_active", False):
        return

    if encounter.catch_ball_visible:
        ball_x, ball_y = encounter.catch_ball_pos
        shadow_rect = pygame.Rect(int(ball_x) - 18, int(ball_y) + 12, 36, 10)
        pygame.draw.ellipse(screen, (0, 0, 0, 85), shadow_rect)
        draw_pokeball(screen, int(ball_x), int(ball_y), 15)

    if encounter.catch_anim_phase == "absorb":
        absorb_progress = encounter.catch_fog_timer
        fog_surface = pygame.Surface((220, 180), pygame.SRCALPHA)
        start_x, start_y = 110, 94
        target_x, target_y = 110, 94
        for index in range(10):
            orbit = index / 10
            curve = math.sin((absorb_progress + orbit) * math.pi)
            offset_x = int(start_x + math.cos(orbit * math.pi * 2) * (52 - absorb_progress * 34))
            offset_y = int(start_y + curve * 24 - absorb_progress * 52)
            radius = max(4, int(24 - absorb_progress * 16 + (index % 3) * 2))
            alpha = max(0, int(190 * (1.0 - absorb_progress * 0.45)))
            pygame.draw.circle(fog_surface, (255, 255, 255, alpha), (offset_x, offset_y), radius)
            trail_x = int(target_x + (offset_x - target_x) * (1.0 - absorb_progress))
            trail_y = int(target_y + (offset_y - target_y) * (1.0 - absorb_progress))
            pygame.draw.circle(fog_surface, (255, 255, 255, max(0, alpha - 50)), (trail_x, trail_y), max(3, radius - 4))
        fog_rect = fog_surface.get_rect(center=(558, 314))
        screen.blit(fog_surface, fog_rect)

    if encounter.catch_anim_phase == "escape" and encounter.catch_fog_timer > 0:
        fog_progress = 1.0 - (encounter.catch_fog_timer / 0.45)
        fog_center_x, fog_center_y = 558, 314
        fog_surface = pygame.Surface((180, 120), pygame.SRCALPHA)
        for index in range(7):
            offset_x = 22 + index * 18
            offset_y = 54 + int(math.sin(index + fog_progress * 8) * 10)
            radius = int(16 + fog_progress * 18 + (index % 3) * 4)
            alpha = max(0, int(190 * (1.0 - fog_progress)))
            pygame.draw.circle(fog_surface, (255, 255, 255, alpha), (offset_x, offset_y), radius)
        fog_rect = fog_surface.get_rect(center=(fog_center_x, fog_center_y))
        screen.blit(fog_surface, fog_rect)

        if encounter.catch_flash_timer > 0:
            flash_progress = 1.0 - (encounter.catch_flash_timer / 0.42)
            burst_surface = pygame.Surface((240, 180), pygame.SRCALPHA)
            burst_alpha = max(0, int(255 * (1.0 - flash_progress)))
            for index in range(7):
                radius = int(18 + flash_progress * 52 + index * 6)
                pygame.draw.circle(
                    burst_surface,
                    (255, 255, 255, max(0, burst_alpha - index * 24)),
                    (120, 90),
                    radius,
                    width=max(1, 4 - index // 2),
                )
            burst_rect = burst_surface.get_rect(center=(fog_center_x, fog_center_y))
            screen.blit(burst_surface, burst_rect)


def draw_battle_trainer_sprite(trainer_name: str, entry_offset: int = 0):
    trainer_sprite = character_back_portraits.get(trainer_name)
    if trainer_sprite is None:
        return

    scaled_sprite = get_cached_transformed_surface(
        trainer_sprite,
        int(trainer_sprite.get_width() * 1.9),
        int(trainer_sprite.get_height() * 1.9),
        smooth=True,
    )
    trainer_rect = scaled_sprite.get_rect(midbottom=(170 - entry_offset, 748))
    shadow_rect = pygame.Rect(trainer_rect.x + 14, trainer_rect.bottom - 12, trainer_rect.width - 28, 12)
    pygame.draw.ellipse(screen, (0, 0, 0, 90), shadow_rect)
    screen.blit(scaled_sprite, trainer_rect)


def setup_new_game(starter_species: Species):
    global pending_player_character, player, world, last_time, last_auto_save, farm_actor_state, selected_farm_pokemon, dragged_farm_pokemon, drag_motion_samples

    fade_out_opening_music()
    starter = Pokemon(starter_species, level=5)
    trainer_name = pending_player_character or "Trainer"
    player = Player(starter, trainer_name)
    world = World(player)
    farm_actor_state = {}
    selected_farm_pokemon = None
    dragged_farm_pokemon = None
    drag_motion_samples = []
    player.inventory = {"potion": 0, "revive": 0, "cure": 0}
    set_status_message(f"{trainer_name} chose {starter_species.name.title()} as a starter.")
    reset_new_game_intro()
    return_to_farm()
    play_farm_music(force=True)
    last_time = time()
    last_auto_save = last_time


def load_game(filename: str) -> bool:
    global player, world, last_time, last_auto_save, farm_actor_state, selected_farm_pokemon, dragged_farm_pokemon, drag_motion_samples

    data = SaveManager.load(resolve_save_file(filename))
    if not data:
        set_status_message("That save slot is empty.")
        return False

    fade_out_opening_music()
    player = Player.from_dict(data)
    world = World(player)
    farm_actor_state = {}
    selected_farm_pokemon = None
    dragged_farm_pokemon = None
    drag_motion_samples = []
    reset_new_game_intro()
    set_status_message("Save file loaded.")
    return_to_farm()
    play_farm_music(force=True)
    last_time = time()
    last_auto_save = last_time
    return True


def set_status_message(message: str, duration: float = 2.5):
    global status_message, status_message_queue, status_message_timer

    if status_message_timer > 0 and message != status_message:
        if not status_message_queue or status_message_queue[-1][0] != message:
            status_message_queue.append((message, duration))
            status_message_queue = status_message_queue[-6:]
        return

    status_message = message
    status_message_timer = duration


def return_to_farm():
    global state

    state = GameState.MAIN_GAME


def show_shop():
    global state

    state = GameState.SHOP


def show_items_bag():
    global state

    state = GameState.ITEMS


def show_party_menu():
    global state, selected_party_pokemon, party_scroll_offset

    if player is not None:
        party_members = player.pokemon_farm
        if selected_party_pokemon not in party_members:
            selected_party_pokemon = player.active_pokemon if party_members else None
        if selected_party_pokemon in party_members:
            selected_index = party_members.index(selected_party_pokemon)
            party_scroll_offset = max(0, min(selected_index, max(0, len(party_members) - 5)))

    state = GameState.PARTY


def show_gym_menu():
    global state

    state = GameState.GYM


def get_gym_opponents() -> list[tuple[str, Species]]:
    if player is None:
        return []

    selected_name = getattr(player, "character_name", None) or pending_player_character or "Henrik"
    opponents: list[tuple[str, Species]] = []
    for name in get_other_character_names(selected_name):
        species = GYM_OPPONENT_TEAMS.get(name, Species.PIDGEOTTO)
        opponents.append((name, species))
    return opponents


def trainer_badge_count() -> int:
    if player is None:
        return 0
    return len([badge for badge in player.gym_badges if badge != GYM_LEADER_NAME])


def gym_leader_unlocked() -> bool:
    return trainer_badge_count() >= 2


def build_gym_cards() -> list[tuple[Button, str, Species, bool, bool]]:
    cards: list[tuple[Button, str, Species, bool, bool]] = []
    for index, (trainer_name, species) in enumerate(get_gym_opponents()):
        x = 42 + index * 246
        button = Button(x, 336, 220, 138, f"Battle {trainer_name}", font)
        earned_badge = player.has_badge(trainer_name) if player is not None else False
        cards.append((button, trainer_name, species, True, earned_badge))

    leader_button = Button(534, 336, 220, 138, f"Battle {GYM_LEADER_NAME}", font)
    leader_earned = player.has_badge(GYM_LEADER_NAME) if player is not None else False
    cards.append((leader_button, GYM_LEADER_NAME, GYM_LEADER_SPECIES, gym_leader_unlocked(), leader_earned))
    return cards


def get_gym_recommended_level(trainer_name: str) -> int:
    if trainer_name == GYM_LEADER_NAME:
        return GYM_LEADER_RECOMMENDED_LEVEL

    opponents = get_gym_opponents()
    for index, (name, _) in enumerate(opponents):
        if name == trainer_name:
            return GYM_RECOMMENDED_LEVELS[min(index, len(GYM_RECOMMENDED_LEVELS) - 1)]
    return GYM_RECOMMENDED_LEVELS[0]


def start_gym_battle(trainer_name: str, species: Species):
    if player is None or world is None:
        return

    level = get_gym_recommended_level(trainer_name)
    world.start_trainer_battle(
        trainer_name,
        species,
        level,
        intro_text=GYM_DIALOGUE.get(trainer_name),
        is_gym_leader=trainer_name == GYM_LEADER_NAME,
    )
    play_gym_music(force=True)
    if trainer_name == GYM_LEADER_NAME:
        play_sound("leader_entrance")
    return_to_farm()


def battle_uses_text(encounter) -> bool:
    return encounter is None or getattr(encounter, "encounter_kind", "wild") == "wild"


def pokemon_throw_weight(pokemon: Pokemon) -> float:
    evolved_species = {
        Species.IVYSAUR,
        Species.VENUSAUR,
        Species.CHARMELEON,
        Species.CHARIZARD,
        Species.WARTORTLE,
        Species.BLASTOISE,
        Species.PIDGEOTTO,
        Species.PIDGEOT,
        Species.RAICHU,
        Species.STARMIE,
        Species.HAUNTER,
        Species.GENGAR,
        Species.JOLTEON,
        Species.FLAREON,
        Species.NINETALES,
        Species.VAPOREON,
        Species.DRAGONAIR,
        Species.MOLTRES,
    }
    evolved_stages = 1 if pokemon.species in evolved_species else 0

    level_weight = min(0.35, pokemon.level * 0.015)
    evolution_weight = evolved_stages * 0.22
    return 1.0 + level_weight + evolution_weight


def maybe_play_bounce_sound(speed: float):
    global last_bounce_sound_time

    current_time = pygame.time.get_ticks() / 1000.0
    if speed < 110 or current_time - last_bounce_sound_time < 0.08:
        return
    play_sound("bounce")
    last_bounce_sound_time = current_time


def create_badge_surface(name: str, unlocked: bool) -> pygame.Surface:
    badge = pygame.Surface((84, 84), pygame.SRCALPHA)
    style = GYM_BADGE_STYLES.get(name, GYM_BADGE_STYLES[GYM_LEADER_NAME])
    fill_color = style["fill"] if unlocked else (34, 40, 52)
    border_color = style["border"] if unlocked else (82, 90, 110)
    shape = style["shape"]

    if shape == "sun":
        center = (42, 42)
        for index in range(8):
            angle = index * (math.pi / 4)
            outer = (42 + int(math.cos(angle) * 34), 42 + int(math.sin(angle) * 34))
            inner_left = (42 + int(math.cos(angle - 0.22) * 20), 42 + int(math.sin(angle - 0.22) * 20))
            inner_right = (42 + int(math.cos(angle + 0.22) * 20), 42 + int(math.sin(angle + 0.22) * 20))
            pygame.draw.polygon(badge, fill_color, [center, inner_left, outer, inner_right])
        pygame.draw.circle(badge, fill_color, center, 20)
        pygame.draw.circle(badge, border_color, center, 20, width=4)
    elif shape == "drop":
        points = [(42, 6), (64, 28), (70, 50), (42, 78), (14, 50), (20, 28)]
        pygame.draw.polygon(badge, fill_color, points)
        pygame.draw.polygon(badge, border_color, points, width=4)
        pygame.draw.circle(badge, fill_color, (42, 42), 18)
    elif shape == "diamond":
        points = [(42, 6), (74, 42), (42, 78), (10, 42)]
        pygame.draw.polygon(badge, fill_color, points)
        pygame.draw.polygon(badge, border_color, points, width=4)
        pygame.draw.line(badge, border_color, (42, 6), (42, 78), 3)
        pygame.draw.line(badge, border_color, (10, 42), (74, 42), 3)
    elif shape == "crown":
        points = [(10, 64), (18, 22), (34, 38), (42, 10), (50, 38), (66, 22), (74, 64)]
        pygame.draw.polygon(badge, fill_color, points)
        pygame.draw.polygon(badge, border_color, points, width=4)
        pygame.draw.rect(badge, fill_color, pygame.Rect(10, 58, 64, 14), border_radius=6)
        pygame.draw.rect(badge, border_color, pygame.Rect(10, 58, 64, 14), width=3, border_radius=6)

    inner_color = (255, 242, 188, 120) if unlocked else (20, 24, 32, 180)
    pygame.draw.circle(badge, inner_color, (42, 42), 14)
    if unlocked:
        initial = tiny_font.render(name[0], True, (88, 54, 8))
        badge.blit(initial, initial.get_rect(center=(42, 42)))
    return badge


def draw_badge_progress():
    badge_names = [name for name, _ in get_gym_opponents()] + [GYM_LEADER_NAME]
    start_x = 164
    for index, badge_name in enumerate(badge_names):
        unlocked = player.has_badge(badge_name) if player is not None else False
        badge_surface = create_badge_surface(badge_name, unlocked)
        badge_x = start_x + index * 156
        screen.blit(badge_surface, (badge_x, 146))
        label = badge_name if badge_name != GYM_LEADER_NAME else "Leader"
        label_color = (250, 240, 200) if unlocked else (130, 142, 160)
        draw_text(screen, label, badge_x + 12, 238, tiny_font, label_color)
        if not unlocked:
            draw_text(screen, "Silhouette", badge_x + 6, 256, tiny_font, (92, 104, 126))


def draw_opponent_trainer_sprite(trainer_name: str, entry_offset: int = 0):
    trainer_sprite = character_portraits.get(trainer_name, create_character_placeholder(trainer_name, 132, 160))
    scaled_sprite = get_cached_transformed_surface(
        trainer_sprite,
        int(trainer_sprite.get_width() * 1.5),
        int(trainer_sprite.get_height() * 1.5),
        smooth=True,
    )
    trainer_rect = scaled_sprite.get_rect(midbottom=(644 + entry_offset, 286))
    shadow_rect = pygame.Rect(trainer_rect.x + 18, trainer_rect.bottom - 10, trainer_rect.width - 36, 12)
    pygame.draw.ellipse(screen, (0, 0, 0, 90), shadow_rect)
    screen.blit(scaled_sprite, trainer_rect)


def draw_trainer_intro(encounter):
    if not getattr(encounter, "intro_active", False):
        return

    panel_rect = pygame.Rect(96, 448, 608, 102)
    shadow = pygame.Surface((panel_rect.width + 12, panel_rect.height + 12), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, 96), shadow.get_rect(), border_radius=20)
    screen.blit(shadow, (panel_rect.x + 6, panel_rect.y + 8))
    pygame.draw.rect(screen, (18, 24, 44), panel_rect, border_radius=20)
    pygame.draw.rect(screen, (188, 214, 255), panel_rect, width=3, border_radius=20)

    speaker = encounter.opponent_name or GYM_LEADER_NAME
    draw_text(screen, speaker, panel_rect.x + 26, panel_rect.y + 18, small_font, (255, 236, 188))
    lines = wrap_text_lines(encounter.intro_text or "", font, 540)
    for index, line in enumerate(lines[:2]):
        draw_text(screen, line, panel_rect.x + 26, panel_rect.y + 44 + index * 24, font, (244, 248, 255))


def draw_versus_card(encounter):
    if player is None:
        return

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((8, 10, 18, 214))
    screen.blit(overlay, (0, 0))

    left_panel = pygame.Rect(70, 120, 250, 250)
    right_panel = pygame.Rect(480, 120, 250, 250)
    center_band = pygame.Rect(288, 140, 224, 200)

    pygame.draw.rect(screen, (18, 28, 54), left_panel, border_radius=24)
    pygame.draw.rect(screen, (90, 170, 255), left_panel, width=3, border_radius=24)
    pygame.draw.rect(screen, (58, 22, 16), right_panel, border_radius=24)
    pygame.draw.rect(screen, (255, 194, 130), right_panel, width=3, border_radius=24)
    pygame.draw.rect(screen, (24, 18, 30), center_band, border_radius=26)
    pygame.draw.rect(screen, (255, 230, 168), center_band, width=3, border_radius=26)

    player_name = player.character_name
    opponent_name = encounter.opponent_name or GYM_LEADER_NAME
    player_portrait = character_portraits.get(player_name, create_character_placeholder(player_name, 132, 160))
    opponent_portrait = character_portraits.get(opponent_name, create_character_placeholder(opponent_name, 132, 160))
    screen.blit(player_portrait, player_portrait.get_rect(center=(left_panel.centerx, left_panel.centery - 22)))
    screen.blit(opponent_portrait, opponent_portrait.get_rect(center=(right_panel.centerx, right_panel.centery - 22)))

    draw_text(screen, player_name, left_panel.x + 70, left_panel.bottom - 44, font, (240, 246, 255))
    draw_text(screen, opponent_name, right_panel.x + 54, right_panel.bottom - 44, font, (255, 236, 214))
    draw_text(screen, "VS", center_band.x + 80, center_band.y + 52, title_font, (255, 224, 140))
    draw_text(screen, encounter.wild.species.name.title(), center_band.x + 44, center_band.y + 116, font, (244, 248, 255))
    draw_text(screen, f"Rec. Lv {get_gym_recommended_level(opponent_name)}", center_band.x + 46, center_band.y + 148, small_font, (210, 226, 255))
    draw_text(screen, "Gym Leader Battle" if getattr(encounter, "is_gym_leader", False) else "Gym Challenger", center_band.x + 28, center_band.y + 178, small_font, (255, 208, 146))


def available_party_pokemon() -> list[Pokemon]:
    if player is None:
        return []
    return [pokemon for pokemon in player.pokemon_farm if not getattr(pokemon, "hospitalized", False)]


def trigger_game_over():
    global selected_farm_pokemon, dragged_farm_pokemon, drag_motion_samples

    selected_farm_pokemon = None
    dragged_farm_pokemon = None
    drag_motion_samples = []
    if world is not None:
        world.current_encounter = None
        play_farm_music(force=True)
    show_game_over_screen("All your Pokémon are in the hospital.")


def sync_party_health_state() -> bool:
    global selected_farm_pokemon

    if player is None:
        return False

    newly_hospitalized: list[Pokemon] = []
    for pokemon in player.pokemon_farm:
        if pokemon.stats.current_hp <= 0 and not getattr(pokemon, "hospitalized", False):
            pokemon.send_to_hospital("This Pokémon has been moved to the hospital.")
            newly_hospitalized.append(pokemon)

    if selected_farm_pokemon is not None and getattr(selected_farm_pokemon, "hospitalized", False):
        selected_farm_pokemon = None

    available_pokemon = available_party_pokemon()
    if not available_pokemon:
        trigger_game_over()
        return True

    if getattr(player.active_pokemon, "hospitalized", False):
        previous_active = player.active_pokemon
        player.active_pokemon = available_pokemon[0]
        if world is not None:
            if world.current_encounter is not None:
                world.current_encounter = None
                play_farm_music(force=True)
        set_status_message(
            f"{previous_active.species.name.title()} was moved to the hospital. {player.active_pokemon.species.name.title()} is now active.",
            duration=3.2,
        )
    elif newly_hospitalized:
        set_status_message(f"{newly_hospitalized[0].species.name.title()} was moved to the hospital.", duration=3.0)

    return False


def build_party_buttons() -> list[Button]:
    if player is None:
        return []

    buttons: list[Button] = []
    visible_party = get_visible_party_pokemon()
    start_y = 214
    for index, pokemon in visible_party:
        label = f"{pokemon.species.name.title()}  Lv.{pokemon.level}"
        if getattr(pokemon, "hospitalized", False):
            label += "  HOSPITAL"
        elif pokemon is player.active_pokemon:
            label += "  ACTIVE"
        button_y = start_y + (index - party_scroll_offset) * 46
        buttons.append(Button(72, button_y, 276, 34, label, tiny_font))
    return buttons


def get_visible_party_pokemon() -> list[tuple[int, Pokemon]]:
    if player is None:
        return []
    end_index = min(len(player.pokemon_farm), party_scroll_offset + 5)
    return list(enumerate(player.pokemon_farm[party_scroll_offset:end_index], start=party_scroll_offset))


def select_party_pokemon(pokemon: Pokemon):
    global selected_party_pokemon

    selected_party_pokemon = pokemon
    set_status_message(f"Selected {pokemon.species.name.title()} in Your Pokemon.", duration=1.5)


def scroll_party_list(direction: int):
    global party_scroll_offset

    if player is None:
        return
    max_offset = max(0, len(player.pokemon_farm) - 5)
    party_scroll_offset = max(0, min(max_offset, party_scroll_offset + direction))

def move_party_pokemon(direction: int):
    """Move selected_party_pokemon up (-1) or down (+1) in the party list."""
    global selected_party_pokemon
    if player is None or selected_party_pokemon is None:
        return
    party = player.pokemon_farm
    idx = party.index(selected_party_pokemon)
    new_idx = idx + direction
    if 0 <= new_idx < len(party):
        party[idx], party[new_idx] = party[new_idx], party[idx]
        selected_party_pokemon = party[new_idx]
        set_status_message(f"Moved {selected_party_pokemon.species.name.title()} {'up' if direction == -1 else 'down'}.", duration=1.2)


def set_active_pokemon(selected_pokemon: Pokemon, return_after: bool = True):
    if player is None:
        return

    if getattr(selected_pokemon, "hospitalized", False):
        set_status_message(f"{selected_pokemon.species.name.title()} is in the hospital and needs a revive.")
        return

    player.active_pokemon = selected_pokemon
    if world is not None and world.current_encounter is not None:
        world.current_encounter.player_pokemon = selected_pokemon
    set_status_message(f"{selected_pokemon.species.name.title()} is now your active Pokémon.")
    if return_after:
        return_to_farm()


def set_selected_farm_pokemon(pokemon: Pokemon):
    global selected_farm_pokemon

    selected_farm_pokemon = pokemon
    set_status_message(f"Selected {pokemon.species.name.title()} for farm care.")


def clear_selected_farm_pokemon(show_message: bool = True):
    global selected_farm_pokemon, dragged_farm_pokemon, drag_motion_samples

    selected_farm_pokemon = None
    dragged_farm_pokemon = None
    drag_motion_samples = []
    if show_message:
        set_status_message("Farm selection cleared.", duration=1.4)


def level_up_selected_farm_pokemon():
    if selected_farm_pokemon is None:
        return

    selected_farm_pokemon.level_up()
    selected_farm_pokemon.display_hp = selected_farm_pokemon.stats.current_hp
    selected_farm_pokemon.display_xp = selected_farm_pokemon.xp
    set_status_message(f"Cheat level up: {selected_farm_pokemon.species.name.title()} is now level {selected_farm_pokemon.level}.")


def evolve_selected_farm_pokemon():
    if selected_farm_pokemon is None:
        return

    if getattr(selected_farm_pokemon, "hospitalized", False):
        set_status_message("That Pokémon is in the hospital and cannot evolve right now.")
        return

    original_species = selected_farm_pokemon.species.name.title()
    if selected_farm_pokemon.start_evolution_animation(force=True):
        set_status_message(f"Cheat evolve: {original_species} is evolving!")
    else:
        selected_farm_pokemon.level_up()
        selected_farm_pokemon.display_hp = selected_farm_pokemon.stats.current_hp
        selected_farm_pokemon.display_xp = selected_farm_pokemon.xp
        set_status_message(
            f"Cheat evolve fallback: {original_species} has no further evolution data, so it gained a free level instead.",
            duration=3.2,
        )


def get_farm_pokemon_at_pos(position: tuple[int, int]) -> Pokemon | None:
    if player is None or world is None or world.current_encounter is not None:
        return None

    for pokemon in reversed(player.pokemon_farm):
        if getattr(pokemon, "hospitalized", False):
            continue
        actor = farm_actor_state.get(id(pokemon))
        if actor is None:
            continue
        pokemon_rect = pygame.Rect(int(float(actor["x"])) - 8, int(float(actor["y"])) - 18, 72, 82)
        if pokemon_rect.collidepoint(position):
            return pokemon
    return None


def buy_item(item_name: str, cost: int, label: str):
    if player is None:
        return

    if player.money < cost:
        set_status_message("You don't have enough money.")
        return

    player.money -= cost
    player.add_item(item_name)
    play_sound("buy")
    set_status_message(f"You bought 1 {label}.")


def use_inventory_item(item_name: str, target_pokemon: Pokemon | None = None):
    if player is None:
        return

    active_pokemon = target_pokemon or selected_party_pokemon or selected_farm_pokemon or player.active_pokemon
    if not player.use_item(item_name):
        set_status_message("That item is not in your bag.")
        return

    if getattr(active_pokemon, "hospitalized", False) and item_name != "revive":
        player.add_item(item_name)
        set_status_message("That Pokémon is in the hospital and needs revive medicine.")
        return

    if item_name == "potion":
        if active_pokemon.stats.current_hp >= active_pokemon.stats.max_hp:
            player.add_item(item_name)
            set_status_message("Your Pokémon already has full HP.")
            return
        active_pokemon.stats.current_hp = min(active_pokemon.stats.max_hp, active_pokemon.stats.current_hp + 30)
        active_pokemon.display_hp = active_pokemon.stats.current_hp
        play_sound("item_used")
        set_status_message(f"You used a potion on {active_pokemon.species.name.title()}.")
    elif item_name == "revive":
        if active_pokemon.stats.current_hp > 0 and not getattr(active_pokemon, "hospitalized", False):
            player.add_item(item_name)
            set_status_message("Revive medicine only works on fainted Pokémon.")
            return
        if getattr(active_pokemon, "hospitalized", False):
            active_pokemon.revive_from_hospital()
            revive_message = f"{active_pokemon.species.name.title()} was revived from the hospital."
        else:
            active_pokemon.stats.current_hp = max(1, active_pokemon.stats.max_hp // 2)
            active_pokemon.display_hp = active_pokemon.stats.current_hp
            revive_message = f"{active_pokemon.species.name.title()} was revived."
        play_sound("item_used")
        set_status_message(revive_message)
    elif item_name == "cure":
        active_pokemon.stats.current_hp = active_pokemon.stats.max_hp
        active_pokemon.display_hp = active_pokemon.stats.current_hp
        play_sound("item_used")
        set_status_message(f"You used a cure on {active_pokemon.species.name.title()} and restored full HP.")


def draw_status_banner():
    if status_message_timer <= 0:
        return

    banner = pygame.Rect(120, 18, 560, 38)
    pygame.draw.rect(screen, (18, 18, 28), banner, border_radius=10)
    pygame.draw.rect(screen, (255, 236, 170), banner, width=2, border_radius=10)
    text_surface = font.render(status_message, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=banner.center)
    screen.blit(text_surface, text_rect)


def draw_farm_text_box(text: str, x: int, y: int, text_font, color=(255, 255, 255), padding_x: int = 8, padding_y: int = 4, bg_color=(10, 16, 24, 110)):
    text_surface = text_font.render(text, True, color)
    background = pygame.Surface((text_surface.get_width() + padding_x * 2, text_surface.get_height() + padding_y * 2), pygame.SRCALPHA)
    pygame.draw.rect(background, bg_color, background.get_rect(), border_radius=8)
    background.blit(text_surface, (padding_x, padding_y))
    screen.blit(background, (x, y))

def draw_need_meter(label: str, value: float, x: int, y: int, width: int = 172):
    clamped_value = max(0.0, min(100.0, float(value)))
    fill_ratio = clamped_value / 100.0
    red = int(255 * (1.0 - fill_ratio) + 90 * fill_ratio)
    green = int(86 + 164 * fill_ratio)
    fill_color = (red, green, 96)

    draw_text(screen, label, x, y, tiny_font, (238, 240, 245))
    draw_text(screen, f"{int(clamped_value)}", x + width + 14, y, tiny_font, (255, 236, 190))
    bar_rect = pygame.Rect(x, y + 18, width, 12)
    pygame.draw.rect(screen, (28, 36, 52), bar_rect, border_radius=6)
    pygame.draw.rect(screen, (190, 214, 255), bar_rect, width=1, border_radius=6)
    fill_width = max(8, int(width * fill_ratio)) if clamped_value > 0 else 0
    if fill_width > 0:
        pygame.draw.rect(screen, fill_color, (bar_rect.x + 1, bar_rect.y + 1, max(1, fill_width - 2), bar_rect.height - 2), border_radius=5)


def format_stat_value(value: float | int) -> str:
    rounded = round(float(value), 2)
    if rounded.is_integer():
        return str(int(rounded))
    return f"{rounded:.2f}"


def pokemon_in_danger(pokemon: Pokemon) -> bool:
    if getattr(pokemon, "hospitalized", False):
        return False
    hp_ratio = pokemon.stats.current_hp / max(1, pokemon.stats.max_hp)
    return pokemon.needs.needs_attention() or hp_ratio <= 0.28


def attention_pokemon() -> list[Pokemon]:
    if player is None:
        return []
    return [pokemon for pokemon in player.pokemon_farm if pokemon_in_danger(pokemon)]


def draw_attention_notification(count: int, x: int, y: int):
    if count <= 0:
        return

    strongest_level = 1
    if attention_pokemon():
        strongest_level = max(danger_level_for_pokemon(pokemon, time()) for pokemon in attention_pokemon())

    pulse = 0.55 + 0.45 * ((math.sin(time() * (6.2 + strongest_level)) + 1.0) / 2.0)
    badge = pygame.Rect(x, y, 118, 36)
    badge_surface = pygame.Surface((badge.width, badge.height), pygame.SRCALPHA)
    fill_red = min(255, 130 + strongest_level * 24)
    pygame.draw.rect(badge_surface, (fill_red, 18, 18, int(176 + 62 * pulse)), badge_surface.get_rect(), border_radius=18)
    pygame.draw.rect(badge_surface, (255, 214, 214, int(210 + 35 * pulse)), badge_surface.get_rect(), width=3, border_radius=18)
    screen.blit(badge_surface, badge.topleft)
    label = f"! {count} alert" if count == 1 else f"! {count} alerts"
    draw_text(screen, label, x + 16, y + 9, tiny_font, (255, 242, 242))


def danger_level_for_pokemon(pokemon: Pokemon, current_time: float) -> int:
    started_at = danger_started_at.get(id(pokemon), current_time)
    elapsed = max(0.0, current_time - started_at)
    return min(4, 1 + int(elapsed // 10))


def maybe_trigger_attention_alert(current_time: float):
    global danger_alert_ids, danger_started_at, last_danger_alert_time

    danger_list = attention_pokemon()
    current_ids = {id(pokemon) for pokemon in danger_list}
    for pokemon in danger_list:
        danger_started_at.setdefault(id(pokemon), current_time)

    for stale_id in list(danger_started_at.keys()):
        if stale_id not in current_ids:
            del danger_started_at[stale_id]

    if current_ids and current_time - last_danger_alert_time >= 5.0:
        highest_level = max(danger_level_for_pokemon(pokemon, current_time) for pokemon in danger_list)
        most_urgent = max(
            danger_list,
            key=lambda pokemon: (
                danger_level_for_pokemon(pokemon, current_time),
                -pokemon.stats.current_hp / max(1, pokemon.stats.max_hp),
            ),
        )
        play_sound("alert", volume_scale=0.72 + highest_level * 0.16)
        if len(danger_list) == 1:
            set_status_message(f"! {most_urgent.species.name.title()} is in danger.", duration=3.1)
        else:
            set_status_message(f"! {len(danger_list)} Pokémon need attention now.", duration=3.1)
        last_danger_alert_time = current_time

    danger_alert_ids = current_ids


def advance_passive_progress(delta: float, current_time: float, update_farm_motion: bool = False) -> bool:
    """Oppdater tidsbasert progresjon som skal skje selv uten direkte input.

    Dette dekker blant annet autosave, animasjoner, encounter-overganger,
    fangstanimasjon og varsler for Pokemon som trenger oppmerksomhet.
    """
    global last_auto_save

    if player is None or world is None:
        return False

    if current_time - last_auto_save >= AUTO_SAVE_INTERVAL:
        SaveManager.save(player.to_dict(), AUTOSAVE_FILE)
        last_auto_save = current_time

    for pokemon in player.pokemon_farm:
        pokemon.tick(delta)
        pokemon.animate(delta)
        pokemon.update_display_hp(delta)

    if update_farm_motion:
        update_farm_wander(delta)

    if world.current_encounter and hasattr(world.current_encounter, "transition"):
        world.current_encounter.transition = max(0.0, world.current_encounter.transition - delta * 2)

    if world.current_encounter:
        world.current_encounter.update_intro(delta)

    if world.current_encounter and getattr(world.current_encounter, "opening_attack_pending", False):
        world.current_encounter.update_opening_attack(delta)

    if world.current_encounter and getattr(world.current_encounter, "attack_sequence_active", False):
        attack_events = world.current_encounter.update_attack_sequence(delta)
        for attack_event in attack_events:
            if attack_event["type"] == "attack_started":
                play_sound("attack")
            elif attack_event["type"] == "attack_hit":
                play_sound("hit")
            elif attack_event["type"] == "turn_finished":
                resolve_attack_round(world.current_encounter)

    if world.current_encounter and getattr(world.current_encounter, "catch_anim_active", False):
        world.current_encounter.update_catch_animation(delta)
        catch_result = world.current_encounter.finish_catch_animation()
        if catch_result == "caught":
            play_sound("catch")
            player.add_pokemon(world.current_encounter.wild)
            player.award_party_xp(world.current_encounter.last_xp_reward)
            set_status_message(
                f"You caught the wild Pokémon, earned ${world.current_encounter.last_money_reward}, and each party Pokémon gained {world.current_encounter.last_xp_reward} XP."
            )
            world.current_encounter = None
            play_farm_music(force=True)
        elif catch_result == "escaped":
            play_sound("hit")
            set_status_message("The wild Pokémon broke free.")

    maybe_trigger_attention_alert(current_time)

    if sync_party_health_state():
        return True

    return False


def resolve_attack_round(encounter):
    if player is None or world is None:
        return

    if encounter.is_over and not encounter.caught:
        if player.active_pokemon.is_fainted():
            set_status_message("Your Pokémon fainted. You returned to the farm.")
        elif getattr(encounter, "encounter_kind", "trainer"):
            earned_new_badge = player.award_badge(encounter.opponent_name or GYM_LEADER_NAME)
            if encounter.opponent_name == GYM_LEADER_NAME and earned_new_badge:
                show_game_over_screen(
                    f"Good job, you beat the game after defeating {GYM_LEADER_NAME}!",
                    title="Congratulations!",
                    is_victory=True,
                    auto_return_delay=14.8,
                )
            elif earned_new_badge:
                set_status_message(
                    f"You defeated {encounter.opponent_name}, earned ${encounter.last_money_reward}, claimed a badge, and each party Pokémon gained {encounter.last_xp_reward} XP!",
                    duration=3.4,
                )
            else:
                set_status_message(
                    f"You defeated {encounter.opponent_name}, earned ${encounter.last_money_reward}, and each party Pokémon gained {encounter.last_xp_reward} XP."
                )
        else:
            set_status_message(
                f"You won the battle, earned ${encounter.last_money_reward}, and each party Pokémon gained {encounter.last_xp_reward} XP."
            )
        world.current_encounter = None
        if not game_over_is_victory:
            play_farm_music(force=True)
    elif encounter.last_effectiveness_text:
        set_status_message(encounter.last_effectiveness_text, duration=1.8)
    elif encounter.last_money_reward > 0:
        set_status_message(f"You earned ${encounter.last_money_reward} from the fight.", duration=1.5)


def clamp_farm_actor_position(actor: dict[str, float | bool]):
    actor["x"] = float(max(FARM_MIN_X, min(FARM_MAX_X, float(actor["x"]))))
    actor["y"] = float(max(FARM_MIN_Y, min(FARM_MAX_Y, float(actor["y"]))))


def ensure_farm_actor(pokemon: Pokemon, index: int):
    actor_key = id(pokemon)
    if actor_key in farm_actor_state:
        return farm_actor_state[actor_key]

    start_x = 80 + (index % 4) * 120 + random.randint(-20, 20)
    start_y = 120 + (index // 4) * 110 + random.randint(-20, 20)
    actor = {
        "x": float(start_x),
        "y": float(start_y),
        "target_x": float(start_x),
        "target_y": float(start_y),
        "speed": float(random.randint(10, 16)),
        "facing_left": False,
        "idle_timer": 0.0,
        "vx": 0.0,
        "vy": 0.0,
        "dragging": False,
        "spin": 0.0,
        "squash": 0.0,
        "landing_timer": 0.0,
    }
    clamp_farm_actor_position(actor)
    farm_actor_state[actor_key] = actor
    return actor


def begin_drag_farm_pokemon(pokemon: Pokemon, mouse_pos: tuple[int, int]):
    global drag_motion_samples, drag_offset, dragged_farm_pokemon

    actor = ensure_farm_actor(pokemon, 0)
    dragged_farm_pokemon = pokemon
    drag_offset = (mouse_pos[0] - float(actor["x"]), mouse_pos[1] - float(actor["y"]))
    actor["dragging"] = True
    actor["vx"] = 0.0
    actor["vy"] = 0.0
    actor["spin"] = 0.0
    actor["squash"] = 0.18
    actor["landing_timer"] = 0.0
    actor["target_x"] = float(actor["x"])
    actor["target_y"] = float(actor["y"])
    timestamp = pygame.time.get_ticks() / 1000.0
    drag_motion_samples = [(timestamp, float(mouse_pos[0]), float(mouse_pos[1]))]


def update_dragged_farm_pokemon(mouse_pos: tuple[int, int]):
    if dragged_farm_pokemon is None:
        return

    actor = farm_actor_state.get(id(dragged_farm_pokemon))
    if actor is None:
        return

    actor["x"] = float(mouse_pos[0] - drag_offset[0])
    actor["y"] = float(mouse_pos[1] - drag_offset[1])
    clamp_farm_actor_position(actor)
    actor["facing_left"] = False
    actor["squash"] = min(0.22, float(actor.get("squash", 0.0)) + 0.02)

    timestamp = pygame.time.get_ticks() / 1000.0
    drag_motion_samples.append((timestamp, float(mouse_pos[0]), float(mouse_pos[1])))
    cutoff = timestamp - 0.12
    while len(drag_motion_samples) > 2 and drag_motion_samples[0][0] < cutoff:
        drag_motion_samples.pop(0)


def release_dragged_farm_pokemon(mouse_pos: tuple[int, int]):
    global drag_motion_samples, dragged_farm_pokemon

    if dragged_farm_pokemon is None:
        return

    actor = farm_actor_state.get(id(dragged_farm_pokemon))
    if actor is None:
        dragged_farm_pokemon = None
        drag_motion_samples = []
        return

    timestamp = pygame.time.get_ticks() / 1000.0
    drag_motion_samples.append((timestamp, float(mouse_pos[0]), float(mouse_pos[1])))
    oldest_time, oldest_x, oldest_y = drag_motion_samples[0]
    newest_time, newest_x, newest_y = drag_motion_samples[-1]
    elapsed = max(0.001, newest_time - oldest_time)
    velocity_x = (newest_x - oldest_x) / elapsed
    velocity_y = (newest_y - oldest_y) / elapsed
    hp_ratio = max(0.2, dragged_farm_pokemon.stats.current_hp / max(1, dragged_farm_pokemon.stats.max_hp))
    condition_factor = 0.35 + hp_ratio * 0.65
    if getattr(dragged_farm_pokemon, "hospitalized", False):
        condition_factor = 0.0
    throw_weight = pokemon_throw_weight(dragged_farm_pokemon)
    condition_factor /= throw_weight
    velocity_x *= condition_factor
    velocity_y *= condition_factor
    max_throw_speed = 980.0 * condition_factor
    velocity_x = max(-max_throw_speed, min(max_throw_speed, velocity_x))
    velocity_y = max(-max_throw_speed, min(max_throw_speed, velocity_y))

    actor["dragging"] = False
    actor["vx"] = velocity_x
    actor["vy"] = velocity_y
    actor["spin"] = velocity_x * 0.045
    actor["squash"] = min(0.26, (abs(velocity_x) + abs(velocity_y)) / 1800)
    actor["target_x"] = float(actor["x"])
    actor["target_y"] = float(actor["y"])
    actor["idle_timer"] = 0.25
    actor["landing_timer"] = 0.0

    if abs(velocity_x) < 55 and abs(velocity_y) < 55:
        actor["vx"] = 0.0
        actor["vy"] = 0.0

    dragged_farm_pokemon = None
    drag_motion_samples = []


def update_farm_wander(delta: float):
    """Gi Pokemon på gården enkel bevegelse, kastfysikk og kollisjoner."""
    global screen_shake_timer

    if player is None or world is None or world.current_encounter is not None:
        return

    visible_farm_pokemon = [pokemon for pokemon in player.pokemon_farm if not getattr(pokemon, "hospitalized", False)]
    valid_keys = {id(pokemon) for pokemon in visible_farm_pokemon}
    for stale_key in list(farm_actor_state.keys()):
        if stale_key not in valid_keys:
            del farm_actor_state[stale_key]

    for index, pokemon in enumerate(visible_farm_pokemon):
        actor = ensure_farm_actor(pokemon, index)
        actor["idle_timer"] = max(0.0, float(actor["idle_timer"]) - delta)

        if bool(actor.get("dragging", False)):
            continue

        velocity_x = float(actor.get("vx", 0.0))
        velocity_y = float(actor.get("vy", 0.0))
        actor["spin"] = float(actor.get("spin", 0.0)) * (0.94 ** max(1.0, delta * 60))
        actor["squash"] = max(0.0, float(actor.get("squash", 0.0)) - delta * 0.85)
        actor["landing_timer"] = max(0.0, float(actor.get("landing_timer", 0.0)) - delta)
        if abs(velocity_x) > 1 or abs(velocity_y) > 1:
            previous_vx = velocity_x
            previous_vy = velocity_y
            actor["x"] = float(actor["x"]) + velocity_x * delta
            actor["y"] = float(actor["y"]) + velocity_y * delta
            bounced = False

            if float(actor["x"]) <= FARM_MIN_X or float(actor["x"]) >= FARM_MAX_X:
                actor["x"] = float(max(FARM_MIN_X, min(FARM_MAX_X, float(actor["x"]))))
                velocity_x *= -0.62
                bounced = True
            if float(actor["y"]) <= FARM_MIN_Y or float(actor["y"]) >= FARM_MAX_Y:
                actor["y"] = float(max(FARM_MIN_Y, min(FARM_MAX_Y, float(actor["y"]))))
                velocity_y *= -0.62
                bounced = True

            if bounced:
                maybe_play_bounce_sound(abs(previous_vx) + abs(previous_vy))
                impact = min(0.28, (abs(previous_vx) + abs(previous_vy)) / 2200)
                actor["squash"] = max(float(actor.get("squash", 0.0)), impact)
                actor["landing_timer"] = 0.18
                actor["spin"] = float(actor.get("spin", 0.0)) * -0.45

            damping = 0.92 ** max(1.0, delta * 60)
            actor["vx"] = velocity_x * damping
            actor["vy"] = velocity_y * damping
            if abs(float(actor["vx"])) < 18:
                actor["vx"] = 0.0
            if abs(float(actor["vy"])) < 18:
                actor["vy"] = 0.0
            if float(actor["vx"]) == 0.0 and float(actor["vy"]) == 0.0 and (abs(previous_vx) > 40 or abs(previous_vy) > 40):
                maybe_play_bounce_sound(abs(previous_vx) + abs(previous_vy))
                actor["landing_timer"] = 0.2
                actor["squash"] = max(float(actor.get("squash", 0.0)), 0.18)
            if abs(velocity_x) > 8:
                actor["facing_left"] = velocity_x < 0
            continue

        dx = float(actor["target_x"]) - float(actor["x"])
        dy = float(actor["target_y"]) - float(actor["y"])
        distance = math.hypot(dx, dy)

        if distance < 4:
            if float(actor["idle_timer"]) <= 0:
                actor["target_x"] = float(random.randint(FARM_MIN_X, FARM_MAX_X))
                actor["target_y"] = float(random.randint(FARM_MIN_Y, FARM_MAX_Y))
                actor["idle_timer"] = float(random.uniform(0.5, 1.8))
        else:
            hp_ratio = max(0.18, pokemon.stats.current_hp / max(1, pokemon.stats.max_hp))
            move_speed = float(actor["speed"]) * (0.3 + 0.7 * hp_ratio)
            step = min(distance, move_speed * delta)
            actor["x"] = float(actor["x"]) + dx / distance * step
            actor["y"] = float(actor["y"]) + dy / distance * step
            clamp_farm_actor_position(actor)
            if abs(dx) > 0.5:
                actor["facing_left"] = dx < 0

    for index, pokemon in enumerate(visible_farm_pokemon):
        actor = ensure_farm_actor(pokemon, index)
        if bool(actor.get("dragging", False)):
            continue
        for other_index in range(index + 1, len(visible_farm_pokemon)):
            other_pokemon = visible_farm_pokemon[other_index]
            other_actor = ensure_farm_actor(other_pokemon, other_index)
            if bool(other_actor.get("dragging", False)):
                continue

            dx = float(other_actor["x"]) - float(actor["x"])
            dy = float(other_actor["y"]) - float(actor["y"])
            distance = math.hypot(dx, dy)
            min_distance = 42.0
            if 0 < distance < min_distance:
                overlap = (min_distance - distance) / 2
                push_x = dx / distance * overlap
                push_y = dy / distance * overlap
                actor["x"] = float(actor["x"]) - push_x
                actor["y"] = float(actor["y"]) - push_y
                other_actor["x"] = float(other_actor["x"]) + push_x
                other_actor["y"] = float(other_actor["y"]) + push_y
                clamp_farm_actor_position(actor)
                clamp_farm_actor_position(other_actor)

                actor_speed = abs(float(actor.get("vx", 0.0))) + abs(float(actor.get("vy", 0.0)))
                other_speed = abs(float(other_actor.get("vx", 0.0))) + abs(float(other_actor.get("vy", 0.0)))
                impact_speed = max(actor_speed, other_speed)
                if impact_speed > 80:
                    maybe_play_bounce_sound(impact_speed)
                    if impact_speed > 420:
                        screen_shake_timer = max(screen_shake_timer, 0.18)
                    actor["vx"] = float(actor.get("vx", 0.0)) * 0.68 - push_x * 8
                    actor["vy"] = float(actor.get("vy", 0.0)) * 0.68 - push_y * 8
                    other_actor["vx"] = float(other_actor.get("vx", 0.0)) * 0.68 + push_x * 8
                    other_actor["vy"] = float(other_actor.get("vy", 0.0)) * 0.68 + push_y * 8
                    actor["landing_timer"] = max(float(actor.get("landing_timer", 0.0)), 0.12)
                    other_actor["landing_timer"] = max(float(other_actor.get("landing_timer", 0.0)), 0.12)
                    actor["squash"] = max(float(actor.get("squash", 0.0)), 0.1)
                    other_actor["squash"] = max(float(other_actor.get("squash", 0.0)), 0.1)


def draw_farm_scene(active_pokemon: Pokemon):
    shake_x = screen_shake_offset[0]
    shake_y = screen_shake_offset[1]
    screen.blit(farm_background, (shake_x, shake_y))

    if player is None:
        return

    battle_time_ms = pygame.time.get_ticks()
    current_time = time()

    visible_farm_pokemon = [pokemon for pokemon in player.pokemon_farm if not getattr(pokemon, "hospitalized", False)]

    for index, pokemon in enumerate(visible_farm_pokemon):
        actor = ensure_farm_actor(pokemon, index)
        sprite = sprite_manager.get_battle_frame(pokemon.species, "front", battle_time_ms)
        if sprite is None:
            continue

        draw_x = int(float(actor["x"])) + shake_x
        draw_y = int(float(actor["y"])) + shake_y
        sprite_size = 56
        if pokemon.evolving:
            sprite_size = max(42, int(56 * pokemon.evo_scale))

        squash = float(actor.get("squash", 0.0))
        stretch_x = 1.0 + squash * 0.55
        stretch_y = 1.0 - squash * 0.35
        scaled_width = max(28, int(sprite_size * stretch_x))
        scaled_height = max(24, int(sprite_size * stretch_y))
        scaled_sprite = get_cached_transformed_surface(
            sprite,
            scaled_width,
            scaled_height,
            flip_horizontal=bool(actor["facing_left"]),
        )
        spin_angle = 0.0 if low_effects_enabled else float(actor.get("spin", 0.0))
        if spin_angle:
            scaled_sprite = pygame.transform.rotozoom(scaled_sprite, -spin_angle, 1.0)

        shadow_rect = pygame.Rect(draw_x + 11, draw_y + 45, 32, 8)
        pygame.draw.ellipse(screen, (0, 0, 0, 90), shadow_rect)
        sprite_pos = (draw_x + (56 - scaled_sprite.get_width()) // 2, draw_y + (56 - scaled_sprite.get_height()) // 2)

        if pokemon_in_danger(pokemon) and not low_effects_enabled:
            danger_level = danger_level_for_pokemon(pokemon, current_time)
            pulse = 0.55 + 0.45 * ((math.sin(current_time * (7.4 + danger_level * 0.9)) + 1.0) / 2.0)
            glow_rect = pygame.Rect(draw_x - 8, draw_y - 8, 72, 72)
            glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.ellipse(
                glow_surface,
                (255, 32, 32, int(72 + 42 * danger_level + 68 * pulse)),
                glow_surface.get_rect(),
            )
            screen.blit(glow_surface, glow_rect.topleft)
            if pulse > 0.58:
                flash_padding = 6 + danger_level * 2
                flash_surface = pygame.Surface((scaled_sprite.get_width() + flash_padding * 2, scaled_sprite.get_height() + flash_padding * 2), pygame.SRCALPHA)
                pygame.draw.rect(
                    flash_surface,
                    (255, 172, 172, min(220, 96 + danger_level * 24)),
                    flash_surface.get_rect(),
                    width=3 + (1 if danger_level >= 3 else 0),
                    border_radius=12,
                )
                screen.blit(flash_surface, (sprite_pos[0] - flash_padding, sprite_pos[1] - flash_padding))

        screen.blit(scaled_sprite, sprite_pos)

        landing_timer = float(actor.get("landing_timer", 0.0))
        if landing_timer > 0 and not low_effects_enabled:
            landing_progress = landing_timer / 0.2
            ring_width = int(26 + (1.0 - landing_progress) * 32)
            ring_height = int(8 + (1.0 - landing_progress) * 8)
            ring_alpha = int(100 * landing_progress)
            ring_surface = pygame.Surface((ring_width + 8, ring_height + 8), pygame.SRCALPHA)
            pygame.draw.ellipse(
                ring_surface,
                (255, 228, 160, ring_alpha),
                pygame.Rect(4, 4, ring_width, ring_height),
                width=2,
            )
            ring_rect = ring_surface.get_rect(center=(draw_x + 28, draw_y + 49))
            screen.blit(ring_surface, ring_rect)

        if pokemon.evolving and not low_effects_enabled:
            glow_size = sprite_size + 16
            glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (255, 255, 200, min(170, pokemon.flash_alpha + 40)), (glow_size // 2, glow_size // 2), glow_size // 2)
            glow_pos = (sprite_pos[0] - (glow_size - sprite_size) // 2, sprite_pos[1] - (glow_size - sprite_size) // 2)
            screen.blit(glow_surface, glow_pos, special_flags=pygame.BLEND_RGBA_ADD)

        if pokemon is selected_farm_pokemon:
            selection_rect = pygame.Rect(draw_x - 4, draw_y - 4, 64, 64)
            pygame.draw.rect(screen, (110, 230, 255), selection_rect, width=3, border_radius=10)

        if pokemon is dragged_farm_pokemon:
            drag_rect = pygame.Rect(draw_x - 8, draw_y - 8, 72, 72)
            pygame.draw.rect(screen, (255, 216, 120), drag_rect, width=2, border_radius=12)

    side_panel_surface = get_farm_side_panel_surface()
    side_panel_x = SCREEN_WIDTH - side_panel_surface.get_width()
    screen.blit(side_panel_surface, (side_panel_x + shake_x, shake_y))

    trainer_name = player.character_name if player is not None else "Trainer"
    scaled_trainer_portrait, portrait_shadow = get_cached_farm_portrait(trainer_name)
    portrait_x = side_panel_x - scaled_trainer_portrait.get_width() - 26
    portrait_y = SCREEN_HEIGHT - int(scaled_trainer_portrait.get_height() * 0.98)
    screen.blit(portrait_shadow, (portrait_x - 10, portrait_y + 8))
    screen.blit(scaled_trainer_portrait, (portrait_x, portrait_y))


def draw_main_menu():
    screen.blit(main_menu_background, (0, 0))
    overlay = get_cached_filled_surface(SCREEN_WIDTH, SCREEN_HEIGHT, (10, 12, 18, 90))
    screen.blit(overlay, (0, 0))
    draw_text(screen, "Pokémon Care Simulator", 245, 96, title_font, (255, 240, 190))
    menu_start_btn.draw(screen)
    menu_load_btn.draw(screen)
    menu_options_btn.draw(screen)
    menu_exit_btn.draw(screen)

    if main_menu_fade_alpha > 0:
        fade_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fade_overlay.fill((0, 0, 0))
        fade_overlay.set_alpha(int(main_menu_fade_alpha))
        screen.blit(fade_overlay, (0, 0))

    draw_status_banner()


def draw_startup_splash():
    screen.fill((0, 0, 0))

    total_fade_in = STARTUP_SPLASH_FADE_IN
    total_hold = STARTUP_SPLASH_HOLD
    fade_out_start = total_fade_in + total_hold
    total_duration = fade_out_start + STARTUP_SPLASH_FADE_OUT

    if startup_splash_timer < total_fade_in:
        logo_alpha = int(255 * min(1.0, startup_splash_timer / total_fade_in))
    elif startup_splash_timer < fade_out_start:
        logo_alpha = 255
    else:
        fade_progress = min(1.0, (startup_splash_timer - fade_out_start) / STARTUP_SPLASH_FADE_OUT)
        logo_alpha = int(255 * (1.0 - fade_progress))

    if startup_logo is not None and logo_alpha > 0:
        logo_surface = startup_logo.copy()
        logo_surface.set_alpha(logo_alpha)
        logo_rect = logo_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 8))
        screen.blit(logo_surface, logo_rect)

        credit_text = tiny_font.render(
            "This game was created in a student assignment by Bjorn Marius.",
            True,
            (214, 224, 236),
        )
        credit_text.set_alpha(int(logo_alpha * 0.88))
        credit_rect = credit_text.get_rect(center=(SCREEN_WIDTH // 2, logo_rect.bottom + 34))
        screen.blit(credit_text, credit_rect)

    if startup_splash_timer >= total_duration - 0.24:
        fade_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fade_overlay.fill((0, 0, 0))
        fade_overlay.set_alpha(int(min(255, ((startup_splash_timer - (total_duration - 0.24)) / 0.24) * 255)))
        screen.blit(fade_overlay, (0, 0))


def draw_load_menu():
    screen.blit(main_menu_background, (0, 0))
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((12, 14, 20, 140))
    screen.blit(overlay, (0, 0))

    draw_text(screen, "Load Game", 354, 120, title_font, (255, 240, 190))
    draw_text(screen, "Choose an autosave or a manual save slot.", 270, 162, small_font, (232, 220, 180))

    load_autosave_btn.text = slot_button_label("Autosave", AUTOSAVE_FILE)
    load_slot_1_btn.text = slot_button_label("Manual Save 1", MANUAL_SAVE_FILES[0])
    load_slot_2_btn.text = slot_button_label("Manual Save 2", MANUAL_SAVE_FILES[1])
    load_slot_3_btn.text = slot_button_label("Manual Save 3", MANUAL_SAVE_FILES[2])

    load_autosave_btn.draw(screen)
    load_slot_1_btn.draw(screen)
    load_slot_2_btn.draw(screen)
    load_slot_3_btn.draw(screen)
    load_back_btn.draw(screen)
    draw_status_banner()


def get_starter_cards() -> list[tuple[Species, Button, pygame.Rect]]:
    starter_buttons = [
        (Species.PIKACHU, pikachu_btn),
        (Species.CHARMANDER, charmander_btn),
        (Species.SQUIRTLE, squirtle_btn),
    ]
    return [
        (species, button, pygame.Rect(button.rect.x - 8, 222, button.rect.width + 16, 116))
        for species, button in starter_buttons
    ]


def get_starter_card_species_at_pos(position: tuple[int, int]) -> Species | None:
    for species, _button, card_rect in get_starter_cards():
        if card_rect.collidepoint(position):
            return species
    return None


def draw_starter_hover_panel(species: Species):
    species_data = POKEMON_DATA[species]
    panel_rect = pygame.Rect(172, 412, 536, 92)
    pygame.draw.rect(screen, (18, 24, 42), panel_rect, border_radius=18)
    pygame.draw.rect(screen, (138, 194, 255), panel_rect, width=2, border_radius=18)

    type_name = species_data["type"].name.replace("_", " ").title()
    draw_text(screen, species.name.title(), panel_rect.x + 18, panel_rect.y + 14, small_font, (255, 242, 190))
    draw_text(screen, f"Type: {type_name}", panel_rect.x + 18, panel_rect.y + 44, tiny_font, (210, 232, 255))
    draw_text(screen, f"HP: {species_data['base_hp']}", panel_rect.x + 168, panel_rect.y + 44, tiny_font, (255, 255, 255))
    draw_text(screen, f"ATK: {species_data['base_attack']}", panel_rect.x + 258, panel_rect.y + 44, tiny_font, (255, 255, 255))
    draw_text(screen, f"DEF: {species_data['base_defense']}", panel_rect.x + 356, panel_rect.y + 44, tiny_font, (255, 255, 255))
    draw_text(screen, f"SPD: {species_data['base_speed']}", panel_rect.x + 456, panel_rect.y + 44, tiny_font, (255, 255, 255))


def draw_game_over_screen():
    latest_file = latest_save_file()
    latest_label = f"Latest save: {save_slot_name(latest_file)}" if latest_file else "No save file found"
    timestamp_label = save_timestamp_label(latest_file)

    panel = pygame.Rect(150, 104, 500, 394)
    panel_fill = (30, 44, 38, 230) if game_over_is_victory else (40, 30, 32, 230)
    panel_border = (156, 214, 162) if game_over_is_victory else (210, 144, 144)
    pygame.draw.rect(screen, panel_fill, panel, border_radius=20)
    pygame.draw.rect(screen, panel_border, panel, width=3, border_radius=20)

    draw_text(screen, game_over_title, 234 if game_over_is_victory else 284, 152, title_font, (255, 244, 190))
    draw_text(screen, game_over_message, 158 if game_over_is_victory else 190, 224, font, (246, 234, 220))

    if game_over_is_victory:
        draw_text(screen, "Congratulations, you're amazing.", 194, 270, small_font, (228, 244, 190))
        draw_text(screen, "Returning to main menu...", 250, 316, small_font, (210, 228, 196))
    else:
        draw_text(screen, "Continue loads the most recent autosave or manual save.", 172, 270, small_font, (228, 204, 190))
        draw_text(screen, latest_label, 270, 302, small_font, (255, 214, 146) if latest_file else (220, 170, 170))
        draw_text(screen, timestamp_label, 220, 330, tiny_font, (234, 214, 194) if latest_file else (220, 170, 170))

        game_over_continue_btn.bg_color = menu_button_color if latest_file else (90, 78, 78)
        game_over_continue_btn.text_color = menu_text_color if latest_file else (180, 170, 170)
        game_over_continue_btn.draw(screen)
        game_over_quit_btn.draw(screen)

    if game_over_fade_alpha > 0:
        fade_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fade_overlay.fill((0, 0, 0))
        fade_overlay.set_alpha(int(game_over_fade_alpha))
        screen.blit(fade_overlay, (0, 0))
    draw_status_banner()


def draw_options_menu():
    screen.fill((28, 30, 52))
    show_game_options = player is not None and options_return_state != GameState.MAIN_MENU
    resolution_scale_btn.text = f"Scale: {int(current_display_scale() * 100)}%"

    draw_text(screen, "Options", 370, 100, title_font, (255, 240, 190))
    draw_text(screen, f"Sound Volume: {sound_volume}", 220, 184, font, (255, 255, 255))
    draw_text(screen, "Muted" if sound_muted else "Active", 760, 184, font, (255, 220, 120))
    sound_vol_down_btn.draw(screen)
    sound_vol_up_btn.draw(screen)
    sound_mute_btn.draw(screen)

    draw_text(screen, f"Music Volume: {music_volume}", 220, 254, font, (255, 255, 255))
    draw_text(screen, "Muted" if music_muted else "Active", 760, 254, font, (255, 220, 120))
    music_vol_down_btn.draw(screen)
    music_vol_up_btn.draw(screen)
    music_mute_btn.draw(screen)
    draw_text(screen, "Resolution Scale", 220, 316, font, (255, 255, 255))
    resolution_scale_btn.draw(screen)
    low_effects_toggle_btn.text = "Low Effects: On" if low_effects_enabled else "Low Effects: Off"
    low_effects_toggle_btn.draw(screen)

    if show_game_options:
        options_main_menu_btn.bg_color = (132, 48, 48)
        options_main_menu_btn.text_color = (255, 236, 236)
        options_save_btn.draw(screen)
        options_load_btn.draw(screen)
        options_main_menu_btn.draw(screen)

    if show_game_options:
        cheats_toggle_btn.text = "Cheats: On" if cheats_enabled else "Cheats: Off"
        cheats_toggle_btn.draw(screen)

    options_back_btn.draw(screen)
    draw_status_banner()


def draw_starter_screen():
    screen.fill((30, 30, 50))
    draw_text(screen, "Choose Your Starter Pokémon", 220, 100, title_font, (255, 255, 200))
    if pending_player_character:
        draw_text(screen, f"{pending_player_character}, pick one to begin your game.", 245, 160, font, (225, 225, 225))
    else:
        draw_text(screen, "Pick one to begin your game.", 290, 160, font, (225, 225, 225))

    starter_cards = get_starter_cards()
    battle_time_ms = pygame.time.get_ticks()
    mouse_pos = get_mouse_pos()
    hovered_species = None
    for species, button, card_rect in starter_cards:
        is_hovered = card_rect.collidepoint(mouse_pos) or button.rect.collidepoint(mouse_pos)
        if is_hovered:
            hovered_species = species
        panel_color = (28, 36, 64) if not is_hovered else (36, 48, 82)
        border_color = (124, 180, 255) if not is_hovered else (184, 224, 255)
        pygame.draw.rect(screen, panel_color, card_rect, border_radius=18)
        pygame.draw.rect(screen, border_color, card_rect, width=3, border_radius=18)

        starter_sprite = sprite_manager.get_battle_frame(species, "front", battle_time_ms)
        if starter_sprite is not None:
            sprite_scale = min(1.3, 72 / max(1, starter_sprite.get_width()), 72 / max(1, starter_sprite.get_height()))
            scaled_starter_sprite = get_cached_transformed_surface(
                starter_sprite,
                max(1, int(starter_sprite.get_width() * sprite_scale)),
                max(1, int(starter_sprite.get_height() * sprite_scale)),
                smooth=True,
            )
            sprite_rect = scaled_starter_sprite.get_rect(center=(card_rect.centerx, card_rect.y + 48))
            screen.blit(scaled_starter_sprite, sprite_rect)

    pikachu_btn.draw(screen)
    charmander_btn.draw(screen)
    squirtle_btn.draw(screen)

    if hovered_species is not None:
        draw_starter_hover_panel(hovered_species)

    if starter_select_fade_alpha > 0:
        fade_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fade_overlay.fill((0, 0, 0))
        fade_overlay.set_alpha(int(starter_select_fade_alpha))
        screen.blit(fade_overlay, (0, 0))

    draw_status_banner()


def draw_intro_sequence_screen():
    screen.blit(main_menu_background, (0, 0))
    atmosphere = get_cached_filled_surface(SCREEN_WIDTH, SCREEN_HEIGHT, (6, 10, 24, 190))
    screen.blit(atmosphere, (0, 0))

    for stripe_y in range(0, SCREEN_HEIGHT, 8):
        pygame.draw.line(screen, (16, 24, 40), (0, stripe_y), (SCREEN_WIDTH, stripe_y), 1)

    draw_text(screen, "A voice cuts through the dark...", 226, 88, small_font, (205, 222, 255))
    if intro_phase in {"dialogue_reveal", "await_continue"}:
        prompt = None
        if intro_phase == "await_continue":
            prompt = "Click or press Enter to continue"
        draw_dialogue_bubble(INTRO_DIALOGUE_TEXT, prompt)

    if intro_overlay_alpha > 0:
        fade_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fade_overlay.fill((0, 0, 0))
        fade_overlay.set_alpha(int(intro_overlay_alpha))
        screen.blit(fade_overlay, (0, 0))


def draw_character_select_screen():
    screen.blit(main_menu_background, (0, 0))
    atmosphere = get_cached_filled_surface(SCREEN_WIDTH, SCREEN_HEIGHT, (8, 14, 28, 198))
    screen.blit(atmosphere, (0, 0))

    draw_dialogue_bubble(INTRO_DIALOGUE_TEXT, None)
    draw_text(screen, "Choose your character", 315, 92, small_font, (220, 236, 255))
    draw_text(screen, "Henrik, Anna, or Martin", 308, 258, font, (235, 242, 255))

    is_ready = intro_phase == "selection_ready"
    if not is_ready:
        draw_text(screen, "The portraits are fading in...", 316, 530, tiny_font, (196, 208, 236))
    else:
        draw_text(screen, "Hover to light them up, then click one.", 284, 530, tiny_font, (196, 224, 255))

    mouse_pos = get_mouse_pos()
    for button in [henrik_character_btn, anna_character_btn, martin_character_btn]:
        portrait = character_portraits[button.text]
        is_hovered = is_ready and button.rect.collidepoint(mouse_pos)
        draw_character_card(button, portrait, is_hovered, is_ready)

    if intro_overlay_alpha > 0:
        fade_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fade_overlay.fill((0, 0, 0))
        fade_overlay.set_alpha(int(intro_overlay_alpha))
        screen.blit(fade_overlay, (0, 0))


def draw_character_briefing_screen():
    if pending_player_character is None:
        return

    screen.blit(main_menu_background, (0, 0))
    atmosphere = get_cached_filled_surface(SCREEN_WIDTH, SCREEN_HEIGHT, (6, 10, 26, 205))
    screen.blit(atmosphere, (0, 0))

    draw_text(screen, "The others step forward", 288, 70, small_font, (214, 232, 255))
    draw_text(screen, f"They look to {pending_player_character}.", 285, 100, tiny_font, (190, 208, 236))

    other_names = get_other_character_names(pending_player_character)
    positions = [148, 532]
    for index, name in enumerate(other_names[:2]):
        draw_briefing_character(name, character_portraits[name], positions[index])

    draw_briefing_dialogue(pending_player_character)
    briefing_accept_btn.draw(screen)

    if intro_overlay_alpha > 0:
        fade_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        fade_overlay.fill((0, 0, 0))
        fade_overlay.set_alpha(int(intro_overlay_alpha))
        screen.blit(fade_overlay, (0, 0))


def draw_shop_screen():
    if player is None:
        return

    alert_count = len(attention_pokemon())

    screen.blit(shop_background, (0, 0))
    overlay = get_cached_filled_surface(SCREEN_WIDTH, SCREEN_HEIGHT, (18, 12, 8, 128))
    screen.blit(overlay, (0, 0))

    panel = pygame.Rect(150, 72, 500, 448)
    panel_surface = get_cached_filled_surface(panel.width, panel.height, (28, 18, 12, 204))
    screen.blit(panel_surface, panel.topleft)
    pygame.draw.rect(screen, (232, 196, 128), panel, width=3, border_radius=24)

    money_badge = pygame.Rect(300, 136, 200, 36)
    pygame.draw.rect(screen, (90, 54, 18), money_badge, border_radius=18)
    pygame.draw.rect(screen, (255, 218, 132), money_badge, width=2, border_radius=18)

    draw_text(screen, "Farm Shop", 320, 98, title_font, (255, 236, 180))
    draw_text(screen, "Stock up before heading back out.", 248, 122, small_font, (230, 220, 208))
    draw_text(screen, f"Money: ${player.money}", 335, 144, font, (255, 220, 90))
    draw_attention_notification(alert_count, 512, 92)

    shop_potion_btn.bg_color = (138, 84, 52)
    shop_revive_btn.bg_color = (126, 58, 58)
    shop_cure_btn.bg_color = (72, 102, 82)
    shop_back_btn.bg_color = (86, 74, 54)

    for button in [shop_potion_btn, shop_revive_btn, shop_cure_btn, shop_back_btn]:
        button.text_color = (248, 238, 220)

    draw_text(screen, "Restore HP for worn-out farm partners.", 232, 248, tiny_font, (226, 212, 194))
    draw_text(screen, "Bring a hospitalized Pokémon back from the clinic.", 196, 328, tiny_font, (226, 212, 194))
    draw_text(screen, "Fully recover a Pokémon in one use.", 246, 408, tiny_font, (226, 212, 194))

    shop_potion_btn.draw(screen)
    shop_revive_btn.draw(screen)
    shop_cure_btn.draw(screen)
    shop_back_btn.draw(screen)
    draw_status_banner()


def draw_items_screen():
    if player is None:
        return

    alert_count = len(attention_pokemon())

    screen.fill((24, 30, 34))
    draw_text(screen, "Bag", 365, 90, title_font, (220, 245, 255))
    draw_attention_notification(alert_count, 512, 84)
    draw_text(screen, f"Potions: {player.inventory.get('potion', 0)}", 295, 160, font, (255, 255, 255))
    draw_text(screen, f"Revive Medicine: {player.inventory.get('revive', 0)}", 255, 240, font, (255, 255, 255))
    draw_text(screen, f"Cure: {player.inventory.get('cure', 0)}", 315, 320, font, (255, 255, 255))
    items_potion_btn.draw(screen)
    items_revive_btn.draw(screen)
    items_cure_btn.draw(screen)
    items_back_btn.draw(screen)
    draw_status_banner()


def draw_party_screen():
    if player is None:
        return

    global selected_party_pokemon, party_scroll_offset

    if selected_party_pokemon not in player.pokemon_farm:
        selected_party_pokemon = player.active_pokemon if player.pokemon_farm else None
    if selected_party_pokemon in player.pokemon_farm:
        selected_index = player.pokemon_farm.index(selected_party_pokemon)
        if selected_index < party_scroll_offset:
            party_scroll_offset = selected_index
        elif selected_index >= party_scroll_offset + 5:
            party_scroll_offset = selected_index - 4

    screen.blit(farm_background, (0, 0))
    overlay = get_cached_filled_surface(SCREEN_WIDTH, SCREEN_HEIGHT, (12, 18, 28, 215))
    screen.blit(overlay, (0, 0))

    draw_text(screen, "Your Pokémon", 286, 56, title_font, (255, 240, 190))
    draw_text(screen, "Choose a Pokémon, then heal, revive, cure, or set it active.", 118, 104, small_font, (230, 230, 230))

    list_panel = pygame.Rect(44, 168, 410, 346)
    detail_panel = pygame.Rect(476, 168, 252, 248)
    pygame.draw.rect(screen, (18, 24, 38), list_panel, border_radius=20)
    pygame.draw.rect(screen, (188, 214, 255), list_panel, width=2, border_radius=20)
    pygame.draw.rect(screen, (22, 30, 44), detail_panel, border_radius=20)
    pygame.draw.rect(screen, (255, 224, 162), detail_panel, width=2, border_radius=20)
    draw_text(screen, "Party", 70, 176, small_font, (255, 236, 188))
    draw_text(screen, f"Showing {party_scroll_offset + 1}-{min(len(player.pokemon_farm), party_scroll_offset + 5)} of {len(player.pokemon_farm)}", 138, 182, tiny_font, (210, 222, 240))

    party_buttons = build_party_buttons()
    visible_party = get_visible_party_pokemon()
    for button, (index, pokemon) in zip(party_buttons, visible_party):
        if getattr(pokemon, "hospitalized", False):
            button.bg_color = (92, 44, 44)
        elif pokemon is selected_party_pokemon:
            button.bg_color = (142, 112, 54)
        elif pokemon is player.active_pokemon:
            button.bg_color = (140, 60, 60)
        else:
            button.bg_color = (70, 80, 120)
        button.draw(screen)

        if getattr(pokemon, "hospitalized", False):
            alert_badge = pygame.Rect(button.rect.x + 12, button.rect.y + 10, 98, 26)
            pygame.draw.rect(screen, (122, 28, 28), alert_badge, border_radius=8)
            pygame.draw.rect(screen, (255, 210, 210), alert_badge, width=2, border_radius=8)
            draw_text(screen, "HOSPITAL", alert_badge.x + 10, alert_badge.y + 5, tiny_font, (255, 236, 236))

            status_panel = pygame.Surface((button.rect.width, button.rect.height), pygame.SRCALPHA)
            status_panel.fill((40, 8, 8, 72))
            screen.blit(status_panel, button.rect.topleft)

        if getattr(pokemon, "hospitalized", False):
            hp_text = "Hospitalized"
        else:
            hp_text = f"HP {format_stat_value(pokemon.stats.current_hp)}/{format_stat_value(pokemon.stats.max_hp)}"
        draw_text(screen, hp_text, 362, button.rect.y + 9, tiny_font, (255, 255, 255))

    if len(player.pokemon_farm) > 5:
        party_scroll_up_btn.draw(screen)
        party_scroll_down_btn.draw(screen)

    focused_pokemon = selected_party_pokemon or player.active_pokemon
    if focused_pokemon is not None:
        info_x = 494
        draw_text(screen, focused_pokemon.species.name.title(), info_x, 188, small_font, (255, 240, 190))
        draw_text(screen, f"Level {focused_pokemon.level}", info_x, 218, tiny_font, (224, 236, 255))
        draw_text(screen, f"HP {format_stat_value(focused_pokemon.stats.current_hp)}/{format_stat_value(focused_pokemon.stats.max_hp)}", info_x, 242, tiny_font, (255, 255, 255))
        draw_text(screen, f"ATK {focused_pokemon.stats.attack}", info_x, 264, tiny_font, (255, 255, 255))
        draw_text(screen, f"DEF {focused_pokemon.stats.defense}", info_x, 286, tiny_font, (255, 255, 255))
        draw_text(screen, f"SPD {focused_pokemon.stats.speed}", info_x, 308, tiny_font, (255, 255, 255))
        if getattr(focused_pokemon, "hospitalized", False):
            draw_text(screen, "Needs revive medicine", info_x, 330, tiny_font, (255, 190, 190))
        elif focused_pokemon is player.active_pokemon:
            draw_text(screen, "Currently active", info_x, 330, tiny_font, (255, 220, 160))

        # Draw item counts to the right of new vertical buttons
        draw_text(screen, f"x{player.inventory.get('potion', 0)}", party_item_start_x + party_item_btn_width + 10, party_item_start_y, tiny_font, (232, 230, 212))
        draw_text(screen, f"x{player.inventory.get('revive', 0)}", party_item_start_x + party_item_btn_width + 10, party_item_start_y + party_item_btn_height + 8, tiny_font, (232, 230, 212))
        draw_text(screen, f"x{player.inventory.get('cure', 0)}", party_item_start_x + party_item_btn_width + 10, party_item_start_y + 2 * (party_item_btn_height + 8), tiny_font, (232, 230, 212))

    party_set_active_btn.draw(screen)
    party_potion_btn.draw(screen)
    party_revive_btn.draw(screen)
    party_cure_btn.draw(screen)

    party_back_btn.rect.topleft = (220, 560)
    party_back_btn.draw(screen)
    draw_status_banner()


def draw_info_screen():
    if player is None:
        return

    screen.blit(farm_background, (0, 0))
    overlay = get_cached_filled_surface(SCREEN_WIDTH, SCREEN_HEIGHT, (10, 16, 26, 225))
    screen.blit(overlay, (0, 0))

    focus_pokemon = selected_farm_pokemon or player.active_pokemon
    focus_type = POKEMON_DATA[focus_pokemon.species]["type"].name.title()
    owned_species = sorted({pokemon.species for pokemon in player.pokemon_farm}, key=lambda species: species.name)

    draw_text(screen, "Info & Pokedex", 270, 40, title_font, (255, 240, 190))
    draw_text(screen, "Species information", 60, 105, small_font, (255, 230, 170))
    draw_text(screen, f"Species: {focus_pokemon.species.name.title()}", 60, 138, small_font, (255, 255, 255))
    draw_text(screen, f"Type: {focus_type}", 60, 168, small_font, (210, 240, 255))
    draw_text(screen, f"Level: {focus_pokemon.level}", 60, 198, small_font, (255, 255, 255))
    draw_text(screen, f"HP: {format_stat_value(focus_pokemon.stats.current_hp)}/{format_stat_value(focus_pokemon.stats.max_hp)}", 60, 228, small_font, (255, 255, 255))
    draw_text(screen, "Selected farm Pokémon is shown here.", 60, 262, tiny_font, (220, 220, 220))
    draw_text(screen, "If none is selected, the battle lead is shown.", 60, 284, tiny_font, (220, 220, 220))

    draw_text(screen, "How to play", 60, 320, small_font, (255, 230, 170))
    draw_text(screen, "1. Click a Pokémon on the farm to care for it.", 60, 352, tiny_font, (230, 230, 230))
    draw_text(screen, "2. Use Feed, Pet, Sleep, and Trip to improve it.", 60, 378, tiny_font, (230, 230, 230))
    draw_text(screen, "3. Trip works like a walk.", 60, 404, tiny_font, (230, 230, 230))
    draw_text(screen, "   Walking trips can start wild encounters.", 60, 426, tiny_font, (230, 230, 230))
    draw_text(screen, "4. In battle, weaken wild Pokémon.", 60, 452, tiny_font, (230, 230, 230))
    draw_text(screen, "   Press Catch to add them to your farm.", 60, 474, tiny_font, (230, 230, 230))

    panel = pygame.Surface((320, 410), pygame.SRCALPHA)
    panel.fill((18, 24, 36, 210))
    screen.blit(panel, (455, 100))
    draw_text(screen, "Pokedex", 565, 118, small_font, (255, 240, 190))
    draw_text(screen, f"Caught: {len(owned_species)} species", 530, 146, tiny_font, (220, 220, 220))

    for index, species in enumerate(owned_species):
        column = index // 8
        row = index % 8
        entry_x = 480 + column * 145
        entry_y = 180 + row * 34
        species_type = POKEMON_DATA[species]["type"].name.title()
        draw_text(screen, species.name.title(), entry_x, entry_y, tiny_font, (255, 255, 255))
        draw_text(screen, species_type, entry_x, entry_y + 16, tiny_font, (160, 225, 255))

    info_back_btn.draw(screen)
    draw_status_banner()


def draw_main_game(delta: float):
    """Tegn enten gården eller kampbildet, avhengig av om spilleren er i encounter."""
    global screen_shake_timer, screen_shake_offset

    if player is None or world is None:
        return

    if screen_shake_timer > 0:
        screen_shake_timer -= delta
        screen_shake_offset[0] = int(5 * math.sin(time() * 60))
        screen_shake_offset[1] = int(5 * math.sin(time() * 40))
    else:
        screen_shake_offset = [0, 0]

    p = player.active_pokemon
    encounter = world.current_encounter

    if getattr(p, "crit", False):
        screen_shake_timer = 0.3
        p.crit = False

    if encounter is None:
        draw_farm_scene(p)
        draw_farm_text_box(f"Battle Lead: {p.species.name.title()}", 16, 16, small_font)
        draw_farm_text_box("Click a Pokemon on the farm to care for it.", 16, 44, tiny_font, (240, 240, 220))
        draw_farm_text_box(f"Money: ${player.money}", 684, 50, small_font, (255, 230, 100))
        draw_farm_text_box(f"Bag: {sum(player.inventory.values())} items", 684, 76, tiny_font, (120, 255, 255))
        draw_farm_text_box("Your Pokemon", 680, 414, tiny_font, (255, 245, 210), padding_x=6, padding_y=3, bg_color=(18, 24, 36, 145))
        draw_farm_text_box("Care Actions", 692, 174, tiny_font, (255, 240, 190), padding_x=8, padding_y=4, bg_color=(24, 30, 46, 150))

        if selected_farm_pokemon is not None:
            selected = selected_farm_pokemon
            info_panel = pygame.Rect(12, 78, 242, 302)
            panel_surface = pygame.Surface((info_panel.width, info_panel.height), pygame.SRCALPHA)
            panel_surface.fill((10, 18, 28, 162))
            screen.blit(panel_surface, info_panel.topleft)
            pygame.draw.rect(screen, (182, 210, 255), info_panel, width=2, border_radius=18)

            draw_farm_text_box(f"Selected: {selected.species.name.title()}", 16, 84, small_font)
            draw_farm_text_box(f"HP: {format_stat_value(selected.stats.current_hp)}/{format_stat_value(selected.stats.max_hp)}", 16, 112, tiny_font)
            draw_farm_text_box(f"Level: {selected.level}", 16, 140, tiny_font)
            draw_health_bar(screen, 20, 164, 148, 14, selected.display_hp, selected.stats.max_hp, selected.hp_shake_offset)

            preview_rect = pygame.Rect(182, 96, 46, 46)
            pygame.draw.rect(screen, (18, 24, 38), preview_rect, border_radius=16)
            pygame.draw.rect(screen, (255, 224, 162), preview_rect, width=2, border_radius=16)
            battle_time_ms = pygame.time.get_ticks()
            selected_sprite = sprite_manager.get_battle_frame(selected.species, "front", battle_time_ms)
            if selected_sprite is not None:
                scaled_preview = get_cached_transformed_surface(selected_sprite, 32, 32, smooth=True)
                preview_sprite_rect = scaled_preview.get_rect(center=preview_rect.center)
                screen.blit(scaled_preview, preview_sprite_rect)
            draw_text(screen, "Needs", 20, 184, tiny_font, (255, 236, 188))

            alert_active = selected.needs.needs_attention() and not getattr(selected, "hospitalized", False)
            alert_bg = (80, 20, 20, 155) if alert_active else (10, 16, 24, 110)

            if alert_active:
                pulse_rect = pygame.Rect(14, 202, 214, 128)
                pygame.draw.rect(screen, alert_bg, pulse_rect, border_radius=16)

            draw_need_meter("Hunger", selected.needs.hunger, 20, 208, width=108)
            draw_need_meter("Happiness", selected.needs.happiness, 20, 238, width=108)
            draw_need_meter("Energy", selected.needs.energy, 20, 268, width=108)
            draw_need_meter("Social", selected.needs.social, 20, 298, width=108)

            if getattr(selected, "hospitalized", False):
                draw_farm_text_box("ALERT: In hospital", 16, 332, tiny_font, (255, 180, 180), bg_color=(96, 24, 24, 180))
                draw_farm_text_box("Use revive medicine to bring it back.", 16, 360, tiny_font, (255, 230, 230), bg_color=(70, 20, 20, 170))
            elif alert_active:
                draw_farm_text_box("ALERT: Needs attention", 16, 332, tiny_font, (255, 200, 200), bg_color=(96, 24, 24, 180))

            exp_ratio = min(1.0, selected.display_xp / max(1, selected.xp_to_next_level()))
            draw_text(screen, f"Experience: {selected.xp}/{selected.xp_to_next_level()}", 20, 350, tiny_font, (244, 228, 164))
            pygame.draw.rect(screen, (22, 34, 92), (20, 370, 148, 12), border_radius=6)
            pygame.draw.rect(screen, (242, 210, 74), (20, 370, int(148 * exp_ratio), 12), border_radius=6)

            if cheats_enabled and not getattr(selected, "hospitalized", False):
                level_up_button.draw(screen)
                evolve_button.draw(screen)

            if not getattr(selected, "hospitalized", False):
                feed_button.draw(screen)
                pet_button.draw(screen)
                sleep_button.draw(screen)
                walk_button.draw(screen)

        gym_button.draw(screen)
        party_button.draw(screen)
        shop_button.draw(screen)
        options_button.draw(screen)
        info_button.draw(screen)
    else:
        screen.blit(battle_background, (0, 0))
        if getattr(encounter, "is_gym_leader", False):
            leader_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            leader_overlay.fill((82, 30, 12, 68))
            screen.blit(leader_overlay, (0, 0))
            if not low_effects_enabled:
                for radius in [120, 190, 270]:
                    pygame.draw.circle(screen, (246, 198, 92), (612, 188), radius, width=3)
        if getattr(encounter, "encounter_kind", "wild") == "trainer" and getattr(encounter, "transition", 0.0) > 0.58:
            draw_versus_card(encounter)
            return
        encounter.wild.update_display_hp(delta)
        w = encounter.wild
        transition_progress = 1.0 - max(0.0, min(1.0, float(getattr(encounter, "transition", 0.0))))
        player_entry_offset = int((1.0 - transition_progress) * 260)
        opponent_entry_offset = int((1.0 - transition_progress) * 280)
        enemy_title = "Wild Pokemon"
        if getattr(encounter, "encounter_kind", "wild") == "trainer":
            enemy_title = f"{encounter.opponent_name or 'Gym'}"
        draw_battle_info_box(enemy_title, w.species.name.title(), 476, 18)
        draw_battle_info_box("HP", f"{format_stat_value(w.stats.current_hp)}/{format_stat_value(w.stats.max_hp)}", 476, 74)
        draw_health_bar(screen, 488, 136, 198, 14, w.display_hp, w.stats.max_hp, w.hp_shake_offset)
        if getattr(encounter, "encounter_kind", "wild") == "wild":
            draw_text(screen, f"Catch: {encounter.catch_difficulty_label()}", 488, 156, tiny_font, (240, 232, 190))

        draw_battle_info_box("Your Pokemon", p.species.name.title(), 72, 174)
        draw_battle_info_box("HP", f"{format_stat_value(p.stats.current_hp)}/{format_stat_value(p.stats.max_hp)}", 72, 230)
        draw_health_bar(screen, 84, 292, 198, 14, p.display_hp, p.stats.max_hp, p.hp_shake_offset)
        if getattr(encounter, "encounter_kind", "wild") == "wild":
            draw_farm_text_box(f"Bag: {sum(player.inventory.values())} items", 78, 316, tiny_font, (220, 245, 255), bg_color=(8, 12, 24, 150))

        battle_time_ms = pygame.time.get_ticks()
        if getattr(encounter, "encounter_kind", "wild") == "trainer":
            draw_opponent_trainer_sprite(encounter.opponent_name or GYM_LEADER_NAME, opponent_entry_offset)
        wild_attack_offset = getattr(encounter, "wild_attack_offset", (0.0, 0.0))
        player_attack_offset = getattr(encounter, "player_attack_offset", (0.0, 0.0))
        wild_sprite = sprite_manager.get_battle_frame(w.species, "front", battle_time_ms)
        hide_wild_sprite = encounter.catch_anim_active and encounter.catch_anim_phase in {"absorb", "blink", "done"}
        if wild_sprite and not hide_wild_sprite:
            scaled_wild_sprite = get_cached_transformed_surface(
                wild_sprite,
                int(wild_sprite.get_width() * 1.08),
                int(wild_sprite.get_height() * 1.08),
                smooth=True,
            )
            screen.blit(
                scaled_wild_sprite,
                (
                    472 + w.shake_offset + opponent_entry_offset + int(wild_attack_offset[0]),
                    204 + w.anim_offset + int(wild_attack_offset[1]),
                ),
            )

        draw_battle_trainer_sprite(player.character_name, player_entry_offset)

        player_sprite = sprite_manager.get_battle_frame(p.species, "back", battle_time_ms)
        if player_sprite:
            scaled_player_sprite = get_cached_transformed_surface(
                player_sprite,
                int(player_sprite.get_width() * 1.72),
                int(player_sprite.get_height() * 1.72),
                smooth=True,
            )
            screen.blit(
                scaled_player_sprite,
                (
                    276 + p.shake_offset - player_entry_offset + int(player_attack_offset[0]),
                    372 + p.anim_offset + int(player_attack_offset[1]),
                ),
            )

        draw_catch_animation(encounter)
        draw_trainer_intro(encounter)

        if not getattr(encounter, "intro_active", False) and not getattr(encounter, "attack_sequence_active", False) and not getattr(encounter, "opening_attack_pending", False):
            attack_button.draw(screen)
        if getattr(encounter, "encounter_kind", "wild") == "wild" and not getattr(encounter, "intro_active", False) and not getattr(encounter, "attack_sequence_active", False) and not getattr(encounter, "opening_attack_pending", False):
            catch_button.draw(screen)
        if not getattr(encounter, "intro_active", False) and not getattr(encounter, "attack_sequence_active", False) and not getattr(encounter, "opening_attack_pending", False):
            items_button.draw(screen)

        if getattr(encounter, "transition", 0) > 0:
            alpha = int(encounter.transition * 255)
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(alpha)
            screen.blit(overlay, (0, 0))

    if battle_uses_text(encounter):
        draw_status_banner()


def draw_gym_screen():
    screen.blit(farm_background, (0, 0))
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((8, 14, 28, 228))
    screen.blit(overlay, (0, 0))

    draw_text(screen, "PokeGym", 308, 34, title_font, (255, 238, 186))
    draw_text(screen, "Challenge the gym and collect badges.", 220, 82, small_font, (212, 232, 255))
    draw_text(screen, f"Win 2 badges to unlock {GYM_LEADER_NAME}.", 242, 108, tiny_font, (188, 212, 238))
    draw_badge_progress()

    gym_buttons = build_gym_cards()
    mouse_pos = get_mouse_pos()
    for button, trainer_name, species, is_unlocked, earned_badge in gym_buttons:
        is_hovered = button.rect.collidepoint(mouse_pos)
        card_rect = button.rect

        shadow = pygame.Surface((card_rect.width + 16, card_rect.height + 16), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 90), shadow.get_rect(), border_radius=24)
        screen.blit(shadow, (card_rect.x + 6, card_rect.y + 8))

        card_hovered = is_hovered and is_unlocked
        panel_color = (18, 34, 66) if not card_hovered else (24, 46, 84)
        border_color = (104, 176, 255) if not card_hovered else (168, 220, 255)
        pygame.draw.rect(screen, panel_color, card_rect, border_radius=22)
        pygame.draw.rect(screen, border_color, card_rect, width=3, border_radius=22)

        portrait = character_portraits.get(trainer_name, create_character_placeholder(trainer_name, 96, 110))
        if not is_unlocked:
            silhouette = portrait.copy()
            silhouette.fill((14, 16, 24, 220), special_flags=pygame.BLEND_RGBA_MULT)
            portrait = silhouette
        portrait_rect = portrait.get_rect(midleft=(card_rect.x + 26, card_rect.centery - 6))
        screen.blit(portrait, portrait_rect)

        draw_text(screen, trainer_name, card_rect.x + 108, card_rect.y + 18, font, (244, 248, 255))
        if is_unlocked:
            recommended_level = get_gym_recommended_level(trainer_name)
            draw_text(screen, f"Pokemon: {species.name.title()}", card_rect.x + 108, card_rect.y + 46, tiny_font, (184, 222, 255))
            draw_text(screen, f"Rec. level: {recommended_level}", card_rect.x + 108, card_rect.y + 68, tiny_font, (255, 232, 196))
            draw_text(screen, "One-on-one gym match", card_rect.x + 108, card_rect.y + 88, tiny_font, (255, 232, 196))
            action_text = "Badge earned" if earned_badge else button.text
            action_color = (214, 255, 194) if earned_badge else (255, 250, 236)
            draw_text(screen, action_text, card_rect.x + 108, card_rect.y + 108, small_font, action_color)
        else:
            draw_text(screen, "Locked", card_rect.x + 108, card_rect.y + 52, small_font, (255, 188, 188))
            draw_text(screen, f"Rec. level: {GYM_LEADER_RECOMMENDED_LEVEL}", card_rect.x + 108, card_rect.y + 74, tiny_font, (208, 208, 214))
            draw_text(screen, "Need 2 badges", card_rect.x + 108, card_rect.y + 94, tiny_font, (208, 208, 214))
            draw_text(screen, "Silhouette only", card_rect.x + 108, card_rect.y + 112, tiny_font, (128, 140, 162))

    gym_back_btn.draw(screen)
    draw_status_banner()


character_portraits = load_character_portraits(CHARACTER_FRONT_ASSET_FILES, 132, 160)
character_portraits[GYM_LEADER_NAME] = load_extra_character_portrait(
    GYM_LEADER_NAME,
    GYM_LEADER_FRONT_ASSET_FILE,
    132,
    160,
)
character_back_portraits = load_character_portraits(CHARACTER_BACK_ASSET_FILES, 150, 212)
character_back_portraits[GYM_LEADER_NAME] = load_extra_character_portrait(
    GYM_LEADER_NAME,
    GYM_LEADER_BACK_ASSET_FILE,
    150,
    212,
)


# Hovedløkken kjører én gang per frame: oppdater lyd, input, spilltilstand og tegning.
while running:
    dt = clock.tick(60) / 1000.0
    now = time()
    delta = now - last_time
    last_time = now

    update_startup_splash(dt)

    if state == GameState.GAME_OVER and game_over_is_victory:
        if game_over_auto_return_timer > 0:
            game_over_auto_return_timer = max(0.0, game_over_auto_return_timer - dt)
            fade_start_time = 1.0
            if game_over_auto_return_timer <= fade_start_time:
                game_over_fade_alpha = min(255.0, 255.0 * (1.0 - (game_over_auto_return_timer / fade_start_time)))
            else:
                game_over_fade_alpha = 0.0
        else:
            return_to_main_menu()
            continue

    if state == GameState.MAIN_MENU and main_menu_fade_alpha > 0:
        main_menu_fade_alpha = max(0.0, main_menu_fade_alpha - 220 * dt)

    update_music_transition()

    if state in {GameState.MAIN_MENU, GameState.LOAD_MENU, GameState.GAME_OVER, GameState.INTRO_SEQUENCE, GameState.CHARACTER_SELECT, GameState.CHARACTER_BRIEFING, GameState.STARTER_SELECT}:
        play_random_opening_music()
    elif player is not None and world is not None and world.current_encounter is not None:
        if getattr(world.current_encounter, "encounter_kind", "wild") == "trainer":
            play_gym_music()
        else:
            play_battle_music()
    elif state == GameState.SHOP and player is not None and world is not None:
        play_shop_music()
    elif state == GameState.OPTIONS and options_return_state == GameState.MAIN_MENU:
        play_random_opening_music()
    elif player is not None and world is not None and state in {GameState.MAIN_GAME, GameState.OPTIONS, GameState.INFO, GameState.PARTY, GameState.GYM, GameState.ITEMS}:
        play_farm_music()

    update_menu_reverb()

    if status_message_timer > 0:
        status_message_timer = max(0.0, status_message_timer - dt)
    elif status_message_queue:
        status_message, status_message_timer = status_message_queue.pop(0)

    if player is not None and state != GameState.GAME_OVER and sync_party_health_state():
        continue

    advance_intro_flow(dt)

    # Samle kun knappene som faktisk er synlige, slik at hover-lyd og klikklogikk blir riktig.
    visible_buttons: list[Button] = []
    if state == GameState.MAIN_MENU:
        visible_buttons = [menu_start_btn, menu_load_btn, menu_options_btn, menu_exit_btn]
    elif state == GameState.LOAD_MENU:
        visible_buttons = [load_autosave_btn, load_slot_1_btn, load_slot_2_btn, load_slot_3_btn, load_back_btn]
    elif state == GameState.OPTIONS:
        visible_buttons = [
            sound_vol_down_btn,
            sound_vol_up_btn,
            sound_mute_btn,
            music_vol_down_btn,
            music_vol_up_btn,
            music_mute_btn,
            resolution_scale_btn,
            low_effects_toggle_btn,
            options_back_btn,
        ]
        if player is not None and options_return_state != GameState.MAIN_MENU:
            visible_buttons.extend([options_save_btn, options_load_btn, options_main_menu_btn, cheats_toggle_btn])
    elif state == GameState.INFO:
        visible_buttons = [info_back_btn]
    elif state == GameState.GYM:
        visible_buttons = [button for button, _, _, is_unlocked, _ in build_gym_cards() if is_unlocked]
        visible_buttons.append(gym_back_btn)
    elif state == GameState.CHARACTER_SELECT and intro_phase == "selection_ready":
        visible_buttons = [henrik_character_btn, anna_character_btn, martin_character_btn]
    elif state == GameState.CHARACTER_BRIEFING and intro_phase == "briefing_ready":
        visible_buttons = [briefing_accept_btn]
    elif state == GameState.STARTER_SELECT:
        visible_buttons = [pikachu_btn, charmander_btn, squirtle_btn]
    elif state == GameState.SHOP:
        visible_buttons = [shop_potion_btn, shop_revive_btn, shop_cure_btn, shop_back_btn]
    elif state == GameState.ITEMS:
        visible_buttons = [items_potion_btn, items_revive_btn, items_cure_btn, items_back_btn]
    elif state == GameState.PARTY:
        visible_buttons = [*build_party_buttons(), party_set_active_btn, party_potion_btn, party_revive_btn, party_cure_btn, party_back_btn]
        if player is not None and len(player.pokemon_farm) > 5:
            visible_buttons.extend([party_scroll_up_btn, party_scroll_down_btn])
    elif state == GameState.MAIN_GAME and player is not None and world is not None:
        if world.current_encounter is None:
            visible_buttons = [party_button, shop_button, gym_button, options_button, info_button]
            if selected_farm_pokemon is not None and not getattr(selected_farm_pokemon, "hospitalized", False):
                visible_buttons.extend([feed_button, pet_button, sleep_button, walk_button])
                if cheats_enabled:
                    visible_buttons.extend([level_up_button, evolve_button])
        else:
            if getattr(world.current_encounter, "catch_anim_active", False) or getattr(world.current_encounter, "attack_sequence_active", False) or getattr(world.current_encounter, "opening_attack_pending", False):
                visible_buttons = []
            else:
                visible_buttons = [] if getattr(world.current_encounter, "intro_active", False) else [attack_button, items_button]
                if getattr(world.current_encounter, "encounter_kind", "wild") == "wild" and not getattr(world.current_encounter, "intro_active", False):
                    visible_buttons.append(catch_button)
    update_hover_sound(visible_buttons)

    # Input håndteres per tilstand for å holde menyer, gård og kamp adskilt.
    for event in pygame.event.get():
        event = normalize_mouse_event(event)
        if event.type == pygame.QUIT:
            running = False

        if state == GameState.SPLASH:
            skip_requested = event.type == pygame.MOUSEBUTTONDOWN
            skip_requested = skip_requested or (event.type == pygame.KEYDOWN and event.key in {pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE})
            if skip_requested:
                finish_startup_splash()

        elif state == GameState.MAIN_MENU:
            if click_button(menu_start_btn, event):
                start_new_game_intro()
            elif click_button(menu_load_btn, event):
                show_load_menu(GameState.MAIN_MENU)
            elif click_button(menu_options_btn, event):
                show_options_menu(GameState.MAIN_MENU)
            elif click_button(menu_exit_btn, event):
                running = False

        elif state == GameState.INTRO_SEQUENCE:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return_to_main_menu()
            elif intro_phase == "await_continue":
                continue_requested = event.type == pygame.MOUSEBUTTONDOWN
                continue_requested = continue_requested or (
                    event.type == pygame.KEYDOWN and event.key in {pygame.K_RETURN, pygame.K_SPACE}
                )
                if continue_requested:
                    play_sound("click")
                    show_character_select()

        elif state == GameState.CHARACTER_SELECT:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return_to_main_menu()
            elif intro_phase == "selection_ready":
                for button in [henrik_character_btn, anna_character_btn, martin_character_btn]:
                    if click_button(button, event):
                        pending_player_character = button.text
                        intro_phase = "selection_fade"
                        intro_phase_timer = 0.0
                        intro_overlay_alpha = 0.0
                        play_sound("intro_transition")
                        break

        elif state == GameState.CHARACTER_BRIEFING:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return_to_main_menu()
            elif intro_phase == "briefing_ready" and click_button(briefing_accept_btn, event):
                total_pages = len(get_briefing_lines(pending_player_character or ""))
                if briefing_page_index < total_pages - 1:
                    briefing_page_index += 1
                else:
                    intro_phase = "briefing_fade"
                    intro_phase_timer = 0.0
                    intro_overlay_alpha = 0.0
                    play_sound("intro_transition")

        elif state == GameState.LOAD_MENU:
            if click_button(load_autosave_btn, event):
                load_game(AUTOSAVE_FILE)
            elif click_button(load_slot_1_btn, event):
                load_game(MANUAL_SAVE_FILES[0])
            elif click_button(load_slot_2_btn, event):
                load_game(MANUAL_SAVE_FILES[1])
            elif click_button(load_slot_3_btn, event):
                load_game(MANUAL_SAVE_FILES[2])
            elif click_button(load_back_btn, event):
                state = load_menu_return_state
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state = load_menu_return_state

        elif state == GameState.GAME_OVER:
            if game_over_is_victory:
                if event.type in {pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN}:
                    game_over_auto_return_timer = min(game_over_auto_return_timer, 0.7)
            else:
                latest_file = latest_save_file()
                if latest_file is not None and click_button(game_over_continue_btn, event):
                    if not continue_from_latest_save():
                        set_status_message("The latest save could not be loaded.")
                elif click_button(game_over_quit_btn, event):
                    return_to_main_menu()
                elif event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if latest_file is not None:
                        if not continue_from_latest_save():
                            set_status_message("The latest save could not be loaded.")
                    else:
                        set_status_message("No autosave or manual save is available.")
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return_to_main_menu()

        elif state == GameState.OPTIONS:
            if click_button(sound_vol_up_btn, event) and sound_volume < 10:
                sound_volume += 1
            elif click_button(sound_vol_down_btn, event) and sound_volume > 1:
                sound_volume -= 1
            elif click_button(sound_mute_btn, event):
                sound_muted = not sound_muted
            elif click_button(music_vol_up_btn, event) and music_volume < 10:
                music_volume += 1
                apply_music_settings()
            elif click_button(music_vol_down_btn, event) and music_volume > 1:
                music_volume -= 1
                apply_music_settings()
            elif click_button(music_mute_btn, event):
                music_muted = not music_muted
                apply_music_settings()
            elif click_button(resolution_scale_btn, event):
                cycle_display_scale()
            elif click_button(low_effects_toggle_btn, event):
                low_effects_enabled = not low_effects_enabled
                set_status_message("Low effects enabled." if low_effects_enabled else "Low effects disabled.")
            elif player is not None and options_return_state != GameState.MAIN_MENU and click_button(options_save_btn, event):
                SaveManager.save(player.to_dict(), MANUAL_SAVE_FILE)
                set_status_message("Game saved.")
            elif player is not None and options_return_state != GameState.MAIN_MENU and click_button(options_load_btn, event):
                show_load_menu(GameState.OPTIONS)
            elif player is not None and options_return_state != GameState.MAIN_MENU and click_button(options_main_menu_btn, event):
                return_to_main_menu()
            elif options_return_state != GameState.MAIN_MENU and click_button(cheats_toggle_btn, event):
                cheats_enabled = not cheats_enabled
                set_status_message("Cheats enabled." if cheats_enabled else "Cheats disabled.")
            elif click_button(options_back_btn, event):
                state = options_return_state
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                state = options_return_state

        elif state == GameState.SHOP:
            if click_button(shop_potion_btn, event):
                buy_item("potion", POTION_COST, "potion")
            elif click_button(shop_revive_btn, event):
                buy_item("revive", REVIVE_COST, "revive medicine")
            elif click_button(shop_cure_btn, event):
                buy_item("cure", CURE_COST, "cure")
            elif click_button(shop_back_btn, event):
                return_to_farm()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return_to_farm()

        elif state == GameState.ITEMS:
            if click_button(items_potion_btn, event):
                use_inventory_item("potion")
            elif click_button(items_revive_btn, event):
                use_inventory_item("revive")
            elif click_button(items_cure_btn, event):
                use_inventory_item("cure")
            elif click_button(items_back_btn, event):
                return_to_farm()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return_to_farm()

        elif state == GameState.PARTY:
            if player is None:
                state = GameState.MAIN_GAME
                continue
            party_buttons = build_party_buttons()
            visible_party = get_visible_party_pokemon()
            handled_party_click = False
            for button, (_, pokemon) in zip(party_buttons, visible_party):
                if click_button(button, event):
                    select_party_pokemon(pokemon)
                    handled_party_click = True
                    break

            if handled_party_click:
                continue
            elif click_button(party_set_active_btn, event):
                if selected_party_pokemon is not None:
                    set_active_pokemon(selected_party_pokemon, return_after=False)
                else:
                    set_status_message("Choose a Pokémon first.")
            elif click_button(party_potion_btn, event):
                if selected_party_pokemon is not None:
                    use_inventory_item("potion", selected_party_pokemon)
                else:
                    set_status_message("Choose a Pokémon first.")
            elif click_button(party_revive_btn, event):
                if selected_party_pokemon is not None:
                    use_inventory_item("revive", selected_party_pokemon)
                else:
                    set_status_message("Choose a Pokémon first.")
            elif click_button(party_cure_btn, event):
                if selected_party_pokemon is not None:
                    use_inventory_item("cure", selected_party_pokemon)
                else:
                    set_status_message("Choose a Pokémon first.")
            elif click_button(party_scroll_up_btn, event):
                if selected_party_pokemon is not None:
                    move_party_pokemon(-1)
                else:
                    scroll_party_list(-1)
            elif click_button(party_scroll_down_btn, event):
                if selected_party_pokemon is not None:
                    move_party_pokemon(1)
                else:
                    scroll_party_list(1)
            elif event.type == pygame.MOUSEWHEEL:
                scroll_party_list(-event.y)
            elif click_button(party_back_btn, event):
                return_to_farm()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return_to_farm()

        elif state == GameState.INFO:
            if click_button(info_back_btn, event):
                return_to_farm()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return_to_farm()

        elif state == GameState.GYM:
            gym_buttons = build_gym_cards()
            handled_gym_click = False
            for button, trainer_name, species, is_unlocked, _ in gym_buttons:
                if is_unlocked and click_button(button, event):
                    start_gym_battle(trainer_name, species)
                    handled_gym_click = True
                    break

            if handled_gym_click:
                continue
            elif click_button(gym_back_btn, event):
                return_to_farm()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return_to_farm()

        elif state == GameState.STARTER_SELECT:
            clicked_starter_species = None
            if event.type == pygame.MOUSEBUTTONDOWN and getattr(event, "button", None) == 1:
                clicked_starter_species = get_starter_card_species_at_pos(event.pos)

            if clicked_starter_species == Species.PIKACHU or click_button(pikachu_btn, event):
                setup_new_game(Species.PIKACHU)
            elif clicked_starter_species == Species.CHARMANDER or click_button(charmander_btn, event):
                setup_new_game(Species.CHARMANDER)
            elif clicked_starter_species == Species.SQUIRTLE or click_button(squirtle_btn, event):
                setup_new_game(Species.SQUIRTLE)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return_to_main_menu()

        elif state == GameState.MAIN_GAME and player is not None and world is not None:
            in_battle = world.current_encounter is not None

            if not in_battle and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and selected_farm_pokemon is not None:
                clear_selected_farm_pokemon()
                continue

            if not in_battle and event.type == pygame.MOUSEBUTTONDOWN and getattr(event, "button", None) == 3 and selected_farm_pokemon is not None:
                clear_selected_farm_pokemon()
                continue

            if not in_battle and event.type == pygame.MOUSEBUTTONDOWN and getattr(event, "button", None) == 1:
                clicked_pokemon = get_farm_pokemon_at_pos(event.pos)
                if clicked_pokemon is not None:
                    if clicked_pokemon is selected_farm_pokemon:
                        play_sound("click")
                        clear_selected_farm_pokemon(show_message=False)
                        set_status_message("Farm selection cleared.", duration=1.4)
                        continue
                    play_sound("click")
                    set_selected_farm_pokemon(clicked_pokemon)
                    begin_drag_farm_pokemon(clicked_pokemon, event.pos)
                    continue
                if selected_farm_pokemon is not None and event.pos[0] < 560 and event.pos[1] < 500:
                    on_hud_button = (
                        level_up_button.rect.collidepoint(event.pos)
                        or evolve_button.rect.collidepoint(event.pos)
                    )
                    if not on_hud_button:
                        clear_selected_farm_pokemon()
                        continue

            if not in_battle and event.type == pygame.MOUSEMOTION and dragged_farm_pokemon is not None:
                update_dragged_farm_pokemon(event.pos)
                continue

            if not in_battle and event.type == pygame.MOUSEBUTTONUP and getattr(event, "button", None) == 1 and dragged_farm_pokemon is not None:
                release_dragged_farm_pokemon(event.pos)
                continue

            if not in_battle and selected_farm_pokemon is not None and not getattr(selected_farm_pokemon, "hospitalized", False) and click_button(feed_button, event):
                selected_farm_pokemon.feed()
                set_status_message(f"You fed {selected_farm_pokemon.species.name.title()}.")
            elif not in_battle and cheats_enabled and selected_farm_pokemon is not None and not getattr(selected_farm_pokemon, "hospitalized", False) and click_button(level_up_button, event):
                level_up_selected_farm_pokemon()
            elif not in_battle and cheats_enabled and selected_farm_pokemon is not None and not getattr(selected_farm_pokemon, "hospitalized", False) and click_button(evolve_button, event):
                evolve_selected_farm_pokemon()
            elif not in_battle and selected_farm_pokemon is not None and not getattr(selected_farm_pokemon, "hospitalized", False) and click_button(pet_button, event):
                selected_farm_pokemon.pet()
                set_status_message(f"You petted {selected_farm_pokemon.species.name.title()}.")
            elif not in_battle and selected_farm_pokemon is not None and not getattr(selected_farm_pokemon, "hospitalized", False) and click_button(sleep_button, event):
                selected_farm_pokemon.sleep(1.0)
                set_status_message(f"{selected_farm_pokemon.species.name.title()} took a nap.")
            elif not in_battle and selected_farm_pokemon is not None and not getattr(selected_farm_pokemon, "hospitalized", False) and click_button(walk_button, event):
                had_encounter = world.current_encounter is not None
                world.walk_step()
                if world.current_encounter is None:
                    set_status_message(
                        f"{selected_farm_pokemon.species.name.title()} took a trip and did not meet any wild Pokémon.",
                        duration=3.8,
                    )
                elif not had_encounter:
                    play_battle_music(force=True)
                    set_status_message(f"A wild {world.current_encounter.wild.species.name.title()} appeared!")
            elif not in_battle and click_button(shop_button, event):
                show_shop()
            elif not in_battle and click_button(gym_button, event):
                show_gym_menu()
            elif not in_battle and click_button(party_button, event):
                show_party_menu()
            elif not in_battle and click_button(options_button, event):
                show_options_menu(GameState.MAIN_GAME)
            elif not in_battle and click_button(info_button, event):
                show_info_menu()

            encounter = world.current_encounter
            if encounter:
                if encounter.catch_anim_active or getattr(encounter, "intro_active", False) or getattr(encounter, "attack_sequence_active", False) or getattr(encounter, "opening_attack_pending", False):
                    continue
                if click_button(attack_button, event):
                    encounter.start_turn_sequence()
                elif getattr(encounter, "encounter_kind", "wild") == "wild" and click_button(catch_button, event):
                    if encounter.start_catch_attempt():
                        play_sound("catch")
                        set_status_message("You threw a Poké Ball!", duration=1.2)
                elif click_button(items_button, event):
                    show_items_bag()

    # Nederst i løkken velges riktig tegnefunksjon for gjeldende spilltilstand.
    if state == GameState.SPLASH:
        draw_startup_splash()
        present_frame()
        continue

    if state == GameState.MAIN_MENU:
        apply_music_settings()
        draw_main_menu()
        present_frame()
        continue

    if state == GameState.LOAD_MENU:
        apply_music_settings()
        draw_load_menu()
        present_frame()
        continue

    if state == GameState.GAME_OVER:
        apply_music_settings()
        draw_game_over_screen()
        present_frame()
        continue

    if state == GameState.INTRO_SEQUENCE:
        apply_music_settings()
        draw_intro_sequence_screen()
        present_frame()
        continue

    if state == GameState.CHARACTER_SELECT:
        apply_music_settings()
        draw_character_select_screen()
        present_frame()
        continue

    if state == GameState.CHARACTER_BRIEFING:
        apply_music_settings()
        draw_character_briefing_screen()
        present_frame()
        continue

    if state == GameState.OPTIONS:
        apply_music_settings()
        draw_options_menu()
        present_frame()
        continue

    if state == GameState.SHOP:
        if advance_passive_progress(delta, now):
            continue
        apply_music_settings()
        draw_shop_screen()
        present_frame()
        continue

    if state == GameState.INFO:
        apply_music_settings()
        draw_info_screen()
        present_frame()
        continue

    if state == GameState.GYM:
        apply_music_settings()
        draw_gym_screen()
        present_frame()
        continue

    if state == GameState.ITEMS:
        if advance_passive_progress(delta, now):
            continue
        apply_music_settings()
        draw_items_screen()
        present_frame()
        continue

    if state == GameState.PARTY:
        apply_music_settings()
        draw_party_screen()
        present_frame()
        continue

    if state == GameState.STARTER_SELECT:
        apply_music_settings()
        draw_starter_screen()
        present_frame()
        continue

    if player is None or world is None:
        state = GameState.MAIN_MENU
        continue

    current_player = player
    current_world = world
    assert current_player is not None
    assert current_world is not None

    if advance_passive_progress(delta, now, update_farm_motion=True):
        continue

    draw_main_game(delta)
    present_frame()

pygame.quit()
sys.exit()