# =============================================================================
# KONFIGURASJON - Mayham Spill
# =============================================================================
# Alle justerbare parametere for spillet samlet på ett sted.
# =============================================================================

# -------------------- SKJERM / DISPLAY --------------------
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600
SCREEN_CENTER_X = SCREEN_WIDTH // 2
SCREEN_CENTER_Y = SCREEN_HEIGHT // 2
FPS = 30
CAPTION = "MayHam"

# -------------------- FPS INNSTILLINGER --------------------
FPS_OPTIONS = [30, 60, 120]  # Tilgjengelige FPS-valg
FPS = 60                    # Gjeldende FPS (startverdi)

# -------------------- LYD INNSTILLINGER --------------------
SOUND_ENABLED = True        # Lyd av/på (True = på)

# -------------------- SPILLER / PLAYER SHIP --------------------
ROTATE_SPEED = 180          # Grader per sekund (venstre/høyre)
THRUST = 220                # Akselerasjon fremover (piksler/s²)
MAX_SPEED = 400             # Maksimal hastighet uten boost
BOOST_MAX = 700             # Maksimal hastighet med boost aktivert
BRAKE = 700                # Bremsekraft (piksler/s²)

# -------------------- VÅPEN / WEAPONS --------------------
LASER_SPEED = 1100          # Laser hastighet (piksler/s)
ENEMY_LASER_SPEED = 720     # Fiende laser hastighet
LASER_LIFETIME = 0.8        # Laser levetid (sekunder) - redusert
ENEMY_LASER_LIFETIME = 1.2  # Fiende laser levetid - redusert
LASER_FIRE_RATE = 0.12      # Tid mellom skudd (sekunder) - redusert

# -------------------- DASH / BOOST --------------------
DASH_SPEED = 1400           # Dash hastighet
DASH_COOLDOWN = 1.2         # Tid mellom dash (sekunder)
DASH_DRAG = 3.2             # Luftmotstand under dash
DASH_DRAG_BOOST = 0.8       # Luftmotstand under dash med boost

# -------------------- DRIVSTOFF / FUEL --------------------
FUEL_MAX = 100.0            # Maksimal drivstoffmengde
FUEL_THRUST_DRAIN = 3.5     # Drivstoffforbruk per sekund (thrust)
FUEL_DASH_COST = 2.5        # Drivstoffkostnad for dash
FUEL_REFILL_RATE = 70.0     # Drivstoffpåfyllingsrate (per sekund)

# -------------------- ROMSTASJON / STATION --------------------
STATION_INTERACT_RADIUS = 170.0  # Radius for å interagere med stasjon
STATION_SPAWN_INTERVAL = 10.0     # Tid mellom stasjonspawn (sekunder) - redusert

# -------------------- FIENDER / ENEMIES --------------------
MAX_WAVE = 200              # Maksimal bølge-nummer
BASE_ENEMY_COUNT = 1        # Grunnantall fiender per bølge
MAX_ENEMIES_PER_WAVE = 6   # Maksimalt antall fiender per bølge (redusert)

# Fiende bølge-skalering
ENEMY_SPEED_BASE = 85       # Base hastighet
ENEMY_SPEED_PER_WAVE = 1.5  # Hastighetsøkning per bølge
ENEMY_SPEED_MAX = 280       # Maksimal fiende hastighet

# Boss-innstillinger
BOSS_HP = 100               # Boss helsepoeng
BOSS_SPEED_BASE = 125      # Boss base hastighet
BOSS_SPEED_PER_WAVE = 0.8  # Boss hastighetsøkning per bølge
BOSS_SCALE = 3.0            # Boss størrelsesfaktor
BOSS_FIRE_RATE = 0.20      # Boss skuddtakt
BOSS_FIRE_CD = 0.8         # Boss skudd cooldown

# -------------------- BAKGRUNN / BACKGROUND --------------------
# Stjerne-lag 1 (fjerne)
STARS_LAYER1_COUNT = 100
STARS_LAYER1_PARALLAX = 0.02

# Stjerne-lag 2 (midtre)
STARS_LAYER2_COUNT = 30
STARS_LAYER2_PARALLAX = 0.06
STARS_LAYER2_TWINKLE_MIN = 0.8
STARS_LAYER2_TWINKLE_MAX = 2.0

# Stjerne-lag 3 (nære)
STARS_LAYER3_COUNT = 10
STARS_LAYER3_PARALLAX = 0.13
STARS_LAYER3_TWINKLE_MIN = 2.0
STARS_LAYER3_TWINKLE_MAX = 4.5

# Bakgrunnsfarge
BG_COLOR = (3, 3, 12)       # Dypt svart-blå rom

# -------------------- BØLGE / WAVE --------------------
WAVE_BANNER_TIME = 2.2      # Tid bølge-banner vises
BOSS_WAVE_INTERVAL = 5      # Hver N. bølge er en boss

# -------------------- SPILL / GAME --------------------
DEATH_TIMER = 1.0           # Tid før spiller gjenoppstår
SCORE_PER_KILL = 10         # Poeng per drept fiende
SCORE_COMET_HIT = -50       # Poengtrekk ved kollisjon med komet
SCORE_PLANET_HIT = -300     # Poengtrekk ved kollisjon med planet/meteor

# -------------------- KOMET / COMET --------------------
COMET_SPAWN_INTERVAL = 15.0   # Tid mellom komet-spawn (sekunder) - redusert
COMET_SPEED = 180            # Komet hastighet
COMET_SIZE = 35              # Komet radius
COMET_COUNT = 3              # Maksimalt antall kometer

# -------------------- LYD / SOUND --------------------
MUSIC_VOLUME = 0.3          # Musikk volum (0.0 - 1.0)
LASER_VOLUME = 0.18         # Laser lyd volum
HOVER_VOLUME = 0.3          # Knapp hover lyd volum
CLICK_VOLUME = 0.3          # Knapp click lyd volum

# -------------------- FONT --------------------
FONT_PATH = "assets/font.ttf"
MENU_FONT_SIZE = 75
TITLE_FONT_SIZE = 45