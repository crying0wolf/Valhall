# Example file showing a circle moving on screen
import sys
import importlib
import math
import random
import pygame

import config

_knapp = importlib.import_module("knapp")
Button = _knapp.Button

# pygame setup
pygame.init()

# Initialize joysticks (controllers)
pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
for joy in joysticks:
    joy.init()

clock = pygame.time.Clock()
clock.tick(config.FPS)
screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
SCREEN = screen
pygame.display.set_caption("Mayham - Main Menu")

# The background. fix tegne bakgrunnen. Ønsker stjener som tegnes utenfor vinduet og ikke for langt unna. Tåke tegnes og planeter.
# bg = screen.fill("orange")


# Lager menyene:
def get_font(size): # Returnerer Press-start-2P i en bestemt størrelse
    return pygame.font.Font("assets/font.ttf", size)

def load_sound(path, volume=0.3):
    try:
        sound = pygame.mixer.Sound(path)
        # Bruk config for lydstyrke og lyd av/på
        effective_volume = volume if getattr(config, 'SOUND_ENABLED', True) else 0
        sound.set_volume(effective_volume)
        return sound
    except (pygame.error, FileNotFoundError):
        return None


CURRENT_MUSIC_TRACK = None


def set_music(track_path, volume=0.3):
    """Setter bakgrunnsmusikk med loop; gjør ingenting hvis samme låt allerede spiller."""
    global CURRENT_MUSIC_TRACK
    try:
        if CURRENT_MUSIC_TRACK != track_path:
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play(-1)
            CURRENT_MUSIC_TRACK = track_path
        # Bruk config for lydstyrke og lyd av/på
        effective_volume = volume if getattr(config, 'SOUND_ENABLED', True) else 0
        pygame.mixer.music.set_volume(effective_volume)
    except (pygame.error, FileNotFoundError):
        pass


def create_background(seed=42):
    rng = random.Random(seed)
    W, H = screen.get_width(), screen.get_height()
    stars = []

    # Lag 1: Fjerne stjerner – mange, bittesmå, svak parallakse
    for _ in range(config.STARS_LAYER1_COUNT):
        b = rng.randint(90, 170)
        stars.append({
            'pos': pygame.Vector2(rng.uniform(0, W), rng.uniform(0, H)),
            'size': 1,
            'color': (b, b, min(255, b + rng.randint(0, 50))),
            'parallax': config.STARS_LAYER1_PARALLAX,
            'twinkle_speed': 0,
            'twinkle_offset': 0,
        })

    # Lag 2: Midtstjerner – litt nærmere, noen flimrer
    for _ in range(config.STARS_LAYER2_COUNT):
        b = rng.randint(170, 225)
        stars.append({
            'pos': pygame.Vector2(rng.uniform(0, W), rng.uniform(0, H)),
            'size': rng.choice([1, 1, 2]),
            'color': (b, b, min(255, b + rng.randint(-10, 40))),
            'parallax': config.STARS_LAYER2_PARALLAX,
            'twinkle_speed': rng.uniform(config.STARS_LAYER2_TWINKLE_MIN, config.STARS_LAYER2_TWINKLE_MAX),
            'twinkle_offset': rng.uniform(0, math.pi * 2),
        })

    # Lag 3: Nærme stjerner – større, flimrer mer
    for _ in range(config.STARS_LAYER3_COUNT):
        b = rng.randint(215, 255)
        stars.append({
            'pos': pygame.Vector2(rng.uniform(0, W), rng.uniform(0, H)),
            'size': rng.randint(2, 3),
            'color': (b, b, min(255, b + rng.randint(0, 30))),
            'parallax': config.STARS_LAYER3_PARALLAX,
            'twinkle_speed': rng.uniform(config.STARS_LAYER3_TWINKLE_MIN, config.STARS_LAYER3_TWINKLE_MAX),
            'twinkle_offset': rng.uniform(0, math.pi * 2),
        })

    # Planeter i verdensrommet (world-koordinater)
    planets = [
        {
            'world': pygame.Vector2(3000, -1800),
            'radius': 85,
            'color': (155, 95, 45),
            'rim': (200, 140, 75),
            'parallax': 0.18,
            'ring': True,
        },
        {
            'world': pygame.Vector2(-3500, 1200),
            'radius': 125,
            'color': (60, 100, 175),
            'rim': (90, 140, 220),
            'parallax': 0.08,
            'ring': False,
        },
        {
            'world': pygame.Vector2(800, 1000),
            'radius': 50,
            'color': (185, 65, 65),
            'rim': (215, 95, 95),
            'parallax': 0.28,
            'ring': False,
        },
        {
            'world': pygame.Vector2(-1500, -4500),
            'radius': 215,
            'color': (130, 155, 105),
            'rim': (165, 190, 135),
            'parallax': 0.05,
            'ring': True,
        },
        {
            'world': pygame.Vector2(2000, -500),
            'radius': 42,
            'color': (175, 175, 215),
            'rim': (205, 205, 235),
            'parallax': 0.22,
            'ring': False,
        },
    ]
    return stars, planets


def draw_background(surface, player_pos, stars, planets, elapsed):
    W, H = surface.get_width(), surface.get_height()
    cx, cy = W // 2, H // 2

    surface.fill((3, 3, 12))  # dypt svart-blå rom

    # Stjerner med parallakse og wrapping
    for star in stars:
        p = star['parallax']
        sx = int(star['pos'].x - player_pos.x * p) % W
        sy = int(star['pos'].y - player_pos.y * p) % H
        color = star['color']
        ts = star['twinkle_speed']
        if ts > 0:
            alpha = 0.58 + 0.42 * math.sin(elapsed * ts + star['twinkle_offset'])
            color = tuple(int(c * alpha) for c in color)
        if star['size'] <= 1:
            surface.set_at((sx, sy), color)
        else:
            pygame.draw.circle(surface, color, (sx, sy), star['size'])

    # Planeter
    for pl in planets:
        p = pl['parallax']
        sx = int(cx + (pl['world'].x - player_pos.x) * p)
        sy = int(cy + (pl['world'].y - player_pos.y) * p)
        r = pl['radius']
        if -r * 4 < sx < W + r * 4 and -r * 4 < sy < H + r * 4:
            if pl['ring']:
                rw, rh = int(r * 4.5), int(r * 0.6)
                ring_surf = pygame.Surface((rw, rh), pygame.SRCALPHA)
                pygame.draw.ellipse(ring_surf, (*pl['rim'], 110), ring_surf.get_rect(), 5)
                surface.blit(ring_surf, (sx - rw // 2, sy - rh // 2))
            pygame.draw.circle(surface, pl['color'], (sx, sy), r)
            pygame.draw.circle(surface, pl['rim'], (sx, sy), r, 2)


# --- Skip-polygon-hjelpere ---

SHIP_COLORS = {1: (80, 200, 255), 2: (255, 160, 60)}


def _trim_alpha(surface):
    """Fjerner tom transparent kant rundt sprite for mer presis skalering/rotasjon."""
    alpha_bounds = surface.get_bounding_rect(min_alpha=1)
    if alpha_bounds.width == 0 or alpha_bounds.height == 0:
        return surface.copy()
    return surface.subsurface(alpha_bounds).copy()


def load_ship_sprites(path="assets/fartoy.png"):
    """Laster spritesheet med to skip side-ved-side: venstre=skip 1, høyre=skip 2."""
    try:
        sheet = pygame.image.load(path).convert_alpha()
    except (pygame.error, FileNotFoundError):
        return {}

    w, h = sheet.get_size()
    if w < 2 or h < 1:
        return {}

    mid = w // 2
    left = _trim_alpha(sheet.subsurface(pygame.Rect(0, 0, mid, h)))
    right = _trim_alpha(sheet.subsurface(pygame.Rect(mid, 0, w - mid, h)))

    # Normaliser til en felles basehøyde så eksisterende scale-verdier fortsatt gir fornuftig størrelse.
    base_h = 64

    def normalize(surface):
        if surface.get_height() <= 0:
            return surface.copy()
        factor = base_h / surface.get_height()
        new_w = max(1, int(surface.get_width() * factor))
        return pygame.transform.smoothscale(surface, (new_w, base_h))

    return {1: normalize(left), 2: normalize(right)}


SHIP_SPRITES = load_ship_sprites()


def load_station_sprite(path="assets/ss.png", target_size=92):
    """Laster og normaliserer romstasjon-sprite brukt ved fuel-fylling."""
    try:
        sprite = pygame.image.load(path).convert_alpha()
    except (pygame.error, FileNotFoundError):
        return None

    sprite = _trim_alpha(sprite)
    if sprite.get_width() <= 0 or sprite.get_height() <= 0:
        return None

    factor = target_size / max(sprite.get_width(), sprite.get_height())
    w = max(1, int(sprite.get_width() * factor))
    h = max(1, int(sprite.get_height() * factor))
    return pygame.transform.smoothscale(sprite, (w, h))


STATION_SPRITE = load_station_sprite()


def load_comet_sprite(path="assets/comet.png", target_size=70):
    """Laster og normaliserer komet-sprite."""
    try:
        sprite = pygame.image.load(path).convert_alpha()
    except (pygame.error, FileNotFoundError):
        return None

    sprite = _trim_alpha(sprite)
    if sprite.get_width() <= 0 or sprite.get_height() <= 0:
        return None

    factor = target_size / max(sprite.get_width(), sprite.get_height())
    w = max(1, int(sprite.get_width() * factor))
    h = max(1, int(sprite.get_height() * factor))
    return pygame.transform.smoothscale(sprite, (w, h))


COMET_SPRITE = load_comet_sprite()


def get_ship_points(ship_id, center, angle_deg, scale=1.0):
    """Returnerer skjermkoordinat-polygon for et skip sentrert på `center`."""
    if ship_id == 1:
        # Fighter: smal og spiss med swept wings
        raw = [
            (0, -35), (7, -10), (22, 14), (9, 7), (7, 28),
            (-7, 28), (-9, 7), (-22, 14), (-7, -10),
        ]
    else:
        # Cruiser: bred og klumpete profil
        raw = [
            (0, -30), (12, -20), (18, -4), (38, 10),
            (30, 22), (14, 28), (-14, 28), (-30, 22),
            (-38, 10), (-18, -4), (-12, -20),
        ]
    rad = math.radians(angle_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    cx, cy = center
    pts = []
    for x, y in raw:
        sx, sy = x * scale, y * scale
        pts.append((cx + sx * cos_a - sy * sin_a, cy + sx * sin_a + sy * cos_a))
    return pts


def draw_ship(surface, ship_id, center, angle_deg, color, scale=1.0):
    """Tegner skip-sprite hvis tilgjengelig, ellers polygon-fallback."""
    sprite = SHIP_SPRITES.get(ship_id)
    if sprite is not None:
        rotated = pygame.transform.rotozoom(sprite, -angle_deg, scale)
        rect = rotated.get_rect(center=(int(center[0]), int(center[1])))
        surface.blit(rotated, rect)
        return

    pts = get_ship_points(ship_id, center, angle_deg, scale)
    pygame.draw.polygon(surface, color, pts)
    dark = tuple(max(0, c - 80) for c in color)
    pygame.draw.polygon(surface, dark, pts, 2)


def play(two_player=False): # Spill skjermen.
    pygame.display.set_caption("MayHam")
    hover_sound = load_sound("assets/hover.wav")
    click_sound = load_sound("assets/click.wav")

    PLAY_BACK = Button(image=None, pos=(config.SCREEN_CENTER_X, 400),
                   text_input="BACK", font=get_font(75), base_color="White", hovering_color="Green", hover_sound=hover_sound, click_sound=click_sound)
    PLAY_BUTTON = Button(image=None, pos=(config.SCREEN_CENTER_X, 300), 
                         text_input="PLAY", font=get_font(75), base_color="#d7fcd4", hovering_color="Yellow", hover_sound=hover_sound, click_sound=click_sound)

    while True:

        PLAY_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.fill("black")

        PLAY_TEXT = get_font(45).render("IN A GALAXY FAR, FAR AWAY...", True, "White")
        PLAY_RECT = PLAY_TEXT.get_rect(center=(config.SCREEN_CENTER_X, 200))
        SCREEN.blit(PLAY_TEXT, PLAY_RECT)

        PLAY_BACK.changeColor(PLAY_MOUSE_POS)
        PLAY_BACK.update(SCREEN)
        PLAY_BUTTON.changeColor(PLAY_MOUSE_POS)
        PLAY_BUTTON.update(SCREEN)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
                    PLAY_BACK.playClick()
                    main_menu()
                if PLAY_BUTTON.checkForInput(PLAY_MOUSE_POS):
                    PLAY_BUTTON.playClick()
                    ship_select(two_player=two_player)

        pygame.display.update()


def ship_select(two_player=False):
    pygame.display.set_caption("Select Your Ship - MAYHAM")
    hover_sound = load_sound("assets/hover.wav")
    click_sound = load_sound("assets/click.wav")

    selected = 1
    preview_angle = 0.0
    ship_was_hovered = {1: False, 2: False}

    SHIP_POS = {1: (config.SCREEN_CENTER_X - 200, config.SCREEN_CENTER_Y), 2: (config.SCREEN_CENTER_X + 200, config.SCREEN_CENTER_Y)}
    HOVER_RADIUS = 115

    BACK_BTN = Button(image=None, pos=(120, config.SCREEN_HEIGHT - 60),
                      text_input="BACK", font=get_font(40), base_color="White",
                      hovering_color="Green", hover_sound=hover_sound, click_sound=click_sound)
    PLAY_BTN = Button(image=None, pos=(config.SCREEN_CENTER_X, config.SCREEN_HEIGHT - 70),
                      text_input="PLAY", font=get_font(60), base_color="#d7fcd4",
                      hovering_color="Yellow", hover_sound=hover_sound, click_sound=click_sound)

    clock = pygame.time.Clock()
    dt = 0.0

    while True:
        mouse_pos = pygame.mouse.get_pos()
        mouse_vec = pygame.Vector2(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for sid, pos in SHIP_POS.items():
                    if pygame.Vector2(pos).distance_to(mouse_vec) < HOVER_RADIUS:
                        if selected != sid:
                            selected = sid
                            if click_sound:
                                click_sound.play()
                if BACK_BTN.checkForInput(mouse_pos):
                    BACK_BTN.playClick()
                    play(two_player=two_player)
                if PLAY_BTN.checkForInput(mouse_pos):
                    PLAY_BTN.playClick()
                    game(selected, two_player=two_player)

        SCREEN.fill((3, 3, 12))

        preview_angle += 35 * dt

        # Tittel
        if two_player:
            title_surf = get_font(52).render("PLAYER 1 - SELECT SHIP", True, "#b68f40")
        else:
            title_surf = get_font(52).render("SELECT YOUR SHIP", True, "#b68f40")
        SCREEN.blit(title_surf, title_surf.get_rect(center=(config.SCREEN_CENTER_X, 60)))

        # Skillelinje
        pygame.draw.line(SCREEN, (40, 40, 70), (config.SCREEN_CENTER_X, 110), (config.SCREEN_CENTER_X, 520), 1)

        for sid, pos in SHIP_POS.items():
            color = SHIP_COLORS[sid]
            is_selected = sid == selected
            is_hovered = pygame.Vector2(pos).distance_to(mouse_vec) < HOVER_RADIUS

            # Hover-lyd
            if is_hovered and not ship_was_hovered[sid]:
                if hover_sound:
                    hover_sound.play()
            ship_was_hovered[sid] = is_hovered

            # Glow ring
            if is_selected:
                pygame.draw.circle(SCREEN, color, pos, HOVER_RADIUS - 8, 3)
                pygame.draw.circle(SCREEN, tuple(c // 3 for c in color), pos, HOVER_RADIUS + 8, 1)
            elif is_hovered:
                pygame.draw.circle(SCREEN, (80, 80, 105), pos, HOVER_RADIUS - 8, 1)

            draw_ship(SCREEN, sid, pos, preview_angle, color, scale=2.6)

            # Etiketter
            label_color = color if is_selected else (140, 140, 155)
            label = get_font(30).render(f"SHIP  {sid}", True, label_color)
            SCREEN.blit(label, label.get_rect(center=(pos[0], pos[1] + 152)))

            if is_selected:
                sel = get_font(20).render("<  SELECTED  >", True, "#d7fcd4")
                SCREEN.blit(sel, sel.get_rect(center=(pos[0], pos[1] + 192)))
            else:
                enemy_lbl = get_font(18).render("WILL BECOME YOUR ENEMY", True, (200, 70, 70))
                SCREEN.blit(enemy_lbl, enemy_lbl.get_rect(center=(pos[0], pos[1] + 192)))

        hint = get_font(20).render("CLICK A SHIP TO SELECT   ·   PLAY TO START", True, (90, 90, 110))
        SCREEN.blit(hint, hint.get_rect(center=(config.SCREEN_CENTER_X, 520)))

        BACK_BTN.changeColor(mouse_pos)
        BACK_BTN.update(SCREEN)
        PLAY_BTN.changeColor(mouse_pos)
        PLAY_BTN.update(SCREEN)

        pygame.display.update()
        dt = clock.tick(config.FPS) / 1000


def options(): # Gir en innstillingsskjerm med tekst og tilbakeknapp.
    pygame.display.set_caption("SETTINGS")
    hover_sound = load_sound("assets/hover.wav")
    click_sound = load_sound("assets/click.wav")

    # Importerer config for innstillinger
    import config

    # Hent lagrede innstillinger eller bruk standard
    sound_enabled = getattr(config, 'SOUND_ENABLED', True)
    current_fps = getattr(config, 'FPS', 60)

    OPTION_BACK = Button(image=None, pos=(config.SCREEN_CENTER_X, config.SCREEN_HEIGHT - 100),
                         text_input="BACK", font=get_font(75), base_color="Yellow", hovering_color="Green", hover_sound=hover_sound, click_sound=click_sound)

    # Lyd av/på knapp
    sound_btn = Button(image=None, pos=(config.SCREEN_CENTER_X, 250),
                      text_input="SOUND: ON" if sound_enabled else "SOUND: OFF",
                      font=get_font(40), base_color="Green" if sound_enabled else "Red",
                      hovering_color="White", hover_sound=hover_sound, click_sound=click_sound)

    # FPS knapper
    fps_btns = []
    fps_labels = ["30", "60", "120"]
    fps_positions = [(config.SCREEN_CENTER_X - 200, 350), (config.SCREEN_CENTER_X, 350), (config.SCREEN_CENTER_X + 200, 350)]
    for i, fps_val in enumerate(fps_labels):
        base_color = "Yellow" if current_fps == int(fps_val) else "White"
        btn = Button(image=None, pos=fps_positions[i],
                     text_input=fps_val, font=get_font(40), base_color=base_color,
                     hovering_color="Green", hover_sound=hover_sound, click_sound=click_sound)
        fps_btns.append(btn)

    while True:
        OPTION_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.fill("black")

        OPTION_TEXT = get_font(45).render("SETTINGS", True, "red")
        OPTION_RECT = OPTION_TEXT.get_rect(center=(config.SCREEN_CENTER_X, 150))
        SCREEN.blit(OPTION_TEXT, OPTION_RECT)

        # Vis lyd status
        sound_text = "ON" if sound_enabled else "OFF"
        sound_color = "Green" if sound_enabled else "Red"
        sound_label = get_font(35).render(f"SOUND: {sound_text}", True, sound_color)
        sound_rect = sound_label.get_rect(center=(config.SCREEN_CENTER_X, 220))
        SCREEN.blit(sound_label, sound_rect)

        # Vis FPS label
        fps_label = get_font(35).render("FPS", True, "White")
        fps_rect = fps_label.get_rect(center=(config.SCREEN_CENTER_X, 300))
        SCREEN.blit(fps_label, fps_rect)

        # Oppdater knapper
        sound_btn.changeColor(OPTION_MOUSE_POS)
        sound_btn.update(SCREEN)

        for btn in fps_btns:
            btn.changeColor(OPTION_MOUSE_POS)
            btn.update(SCREEN)

        OPTION_BACK.changeColor(OPTION_MOUSE_POS)
        OPTION_BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if sound_btn.checkForInput(OPTION_MOUSE_POS):
                    sound_btn.playClick()
                    # Toggle lyd
                    sound_enabled = not sound_enabled
                    config.SOUND_ENABLED = sound_enabled
                    # Oppdater lyd volum basert på status
                    pygame.mixer.music.set_volume(config.MUSIC_VOLUME if sound_enabled else 0)
                for i, btn in enumerate(fps_btns):
                    if btn.checkForInput(OPTION_MOUSE_POS):
                        btn.playClick()
                        # Sett ny FPS
                        new_fps = config.FPS_OPTIONS[i]
                        config.FPS = new_fps
                        current_fps = new_fps
                if OPTION_BACK.checkForInput(OPTION_MOUSE_POS):
                    OPTION_BACK.playClick()
                    main_menu()

        pygame.display.update()



def main_menu(): # En hovedmeny skjerm.
    pygame.display.set_caption("main_menu")
    set_music("assets/m/Stellar Menu Drift.mp3", volume=0.33)

    BUTTON_IMAGE = pygame.transform.scale(pygame.image.load("assets/Play Rect.png"), (520, 380))
    hover_sound = load_sound("assets/hover.wav")
    click_sound = load_sound("assets/click.wav")

    SINGLE_BUTTON = Button(image=BUTTON_IMAGE, pos=(config.SCREEN_CENTER_X, config.SCREEN_CENTER_Y - 50), 
                           text_input="SINGLE PLAYER", font=get_font(40), base_color="#d7fcd4", hovering_color="White", hover_sound=hover_sound, click_sound=click_sound)
    MULTI_BUTTON = Button(image=BUTTON_IMAGE, pos=(config.SCREEN_CENTER_X, config.SCREEN_CENTER_Y + 80), 
                          text_input="TWO PLAYERS", font=get_font(40), base_color="#d7fcd4", hovering_color="White", hover_sound=hover_sound, click_sound=click_sound)
    OPTIONS_BUTTON = Button(image=BUTTON_IMAGE, pos=(config.SCREEN_CENTER_X, config.SCREEN_CENTER_Y + 210), 
                            text_input="OPTIONS", font=get_font(50), base_color="#d7fcd4", hovering_color="White", hover_sound=hover_sound, click_sound=click_sound)

    while True:
        SCREEN.fill("black")

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(100).render("MAYHAM X", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(config.SCREEN_CENTER_X, 100))

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [SINGLE_BUTTON, MULTI_BUTTON, OPTIONS_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if SINGLE_BUTTON.checkForInput(MENU_MOUSE_POS):
                    SINGLE_BUTTON.playClick()
                    play()
                if MULTI_BUTTON.checkForInput(MENU_MOUSE_POS):
                    MULTI_BUTTON.playClick()
                    play(two_player=True)
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    OPTIONS_BUTTON.playClick()
                    options()
        pygame.display.update()

def game(selected_ship=1, two_player=False):
    set_music("assets/m/space vortex.mp3", volume=0.22)
    clock = pygame.time.Clock()
    running = True
    dt = 0

    # Re-init joysticks for this game session
    pygame.joystick.init()
    game_joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    for joy in game_joysticks:
        joy.init()

    # Spiller 1
    world_pos = pygame.Vector2(0, 0)
    velocity = pygame.Vector2(0, 0)
    angle = 0
    boost = False
    elapsed = 0
    cx = screen.get_width() // 2
    cy = screen.get_height() // 2
    screen_center = pygame.Vector2(cx, cy)
    stars, planets = create_background()

    player_color = SHIP_COLORS[selected_ship]
    enemy_ship_id = 3 - selected_ship
    enemy_color = (220, 60, 60)

    # Spiller 2 (kun i 2-player modus)
    player2_active = False
    if two_player:
        player2_active = True
        world_pos2 = pygame.Vector2(0, 0)
        velocity2 = pygame.Vector2(0, 0)
        angle2 = 0
        boost2 = False
        fuel2 = config.FUEL_MAX
        player_hits2 = 0
        player_dead2 = False
        dash_timer2 = config.DASH_COOLDOWN
        dashing2 = False
        lasers2 = []
        fire_timer2 = 0
        selected_ship2 = 2 if selected_ship == 1 else 1
        player_color2 = SHIP_COLORS[selected_ship2]
        screen_center2 = pygame.Vector2(cx - 80, cy + 80)  # Offset for spiller 2

    ROTATE_SPEED = config.ROTATE_SPEED
    THRUST = config.THRUST
    BRAKE = config.BRAKE
    MAX_SPEED = config.MAX_SPEED
    BOOST_MAX = config.BOOST_MAX

    DASH_SPEED = config.DASH_SPEED
    DASH_COOLDOWN = config.DASH_COOLDOWN
    DASH_DRAG = config.DASH_DRAG
    DASH_DRAG_BOOST = config.DASH_DRAG_BOOST
    dash_timer = config.DASH_COOLDOWN
    dashing = False

    LASER_SPEED = config.LASER_SPEED
    ENEMY_LASER_SPEED = config.ENEMY_LASER_SPEED
    LASER_LIFETIME = config.LASER_LIFETIME
    ENEMY_LASER_LIFETIME = config.ENEMY_LASER_LIFETIME
    LASER_FIRE_RATE = config.LASER_FIRE_RATE
    laser_sound = load_sound("assets/laser.wav", volume=0.18)
    lasers = []
    enemy_lasers = []
    fire_timer = 0

    MAX_WAVE = config.MAX_WAVE
    wave = 1
    score = 0
    player_hits = 0
    player_dead = False
    death_timer = config.DEATH_TIMER
    enemies = []
    wave_banner_timer = config.WAVE_BANNER_TIME
    between_waves = False
    wave_countdown = 0

    fuel = config.FUEL_MAX
    station_spawn_timer = 0.0
    stations = []

    # Kometer
    COMET_SPAWN_INTERVAL = config.COMET_SPAWN_INTERVAL
    COMET_SPEED = config.COMET_SPEED
    COMET_SIZE = config.COMET_SIZE
    COMET_COUNT = config.COMET_COUNT
    COMET_SCORE_PENALTY = config.SCORE_COMET_HIT
    comet_spawn_timer = 0.0
    comets = []

    # Fuel settings
    FUEL_DASH_COST = config.FUEL_DASH_COST
    FUEL_THRUST_DRAIN = config.FUEL_THRUST_DRAIN
    FUEL_REFILL_RATE = config.FUEL_REFILL_RATE
    STATION_INTERACT_RADIUS = config.STATION_INTERACT_RADIUS
    STATION_SPAWN_INTERVAL = config.STATION_SPAWN_INTERVAL

    def to_roman(num):
        values = [
            (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
            (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
            (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I'),
        ]
        out = []
        n = int(max(1, num))
        for v, sym in values:
            while n >= v:
                out.append(sym)
                n -= v
        return ''.join(out)

    def to_roman_visual(num):
        # Bruk egne romertall-glyfer for tydeligere visning enn vanlige bokstaver.
        glyph_map = str.maketrans({
            'I': 'Ⅰ', 'V': 'Ⅴ', 'X': 'Ⅹ', 'L': 'Ⅼ', 'C': 'Ⅽ', 'D': 'Ⅾ', 'M': 'Ⅿ'
        })
        return to_roman(num).translate(glyph_map)

    def spawn_wave(wave_number):
        spawned = []
        is_boss_wave = (wave_number % config.BOSS_WAVE_INTERVAL == 0)

        if is_boss_wave:
            spawn_angle = random.uniform(0, 360)
            spawn_dist = random.uniform(1300, 1800)
            pos = world_pos + pygame.Vector2(0, -1).rotate(spawn_angle) * spawn_dist
            spawned.append({
                'pos': pos,
                'vel': pygame.Vector2(0, 0),
                'hp': config.BOSS_HP,
                'max_hp': config.BOSS_HP,
                'fire_cd': config.BOSS_FIRE_CD,
                'fire_rate': config.BOSS_FIRE_RATE,
                'speed': config.BOSS_SPEED_BASE + min(80, wave_number * config.BOSS_SPEED_PER_WAVE),
                'scale': config.BOSS_SCALE,
                'boss': True,
                'angle': 180,
            })
            return spawned

        count = min(config.BASE_ENEMY_COUNT + wave_number // 2, config.MAX_ENEMIES_PER_WAVE)
        for _ in range(count):
            spawn_angle = random.uniform(0, 360)
            spawn_dist = random.uniform(900, 1700)
            pos = world_pos + pygame.Vector2(0, -1).rotate(spawn_angle) * spawn_dist
            hp = random.randint(1, 3)
            spawned.append({
                'pos': pos,
                'vel': pygame.Vector2(0, 0),
                'hp': hp,
                'max_hp': hp,
                'fire_cd': random.uniform(0.5, 2.1),
                'fire_rate': max(0.28, 1.5 - wave_number * 0.004),
                'speed': min(config.ENEMY_SPEED_MAX, config.ENEMY_SPEED_BASE + wave_number * config.ENEMY_SPEED_PER_WAVE),
                'scale': 1.35,
                'boss': False,
                'angle': 180,
            })
        return spawned

    enemies = spawn_wave(wave)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                    boost = True
                if event.key == pygame.K_SPACE and dash_timer >= DASH_COOLDOWN and not player_dead:
                    if fuel >= FUEL_DASH_COST:
                        dash_dir = pygame.Vector2(0, -1).rotate(angle)
                        velocity = dash_dir * DASH_SPEED
                        dash_timer = 0
                        dashing = True
                        fuel -= FUEL_DASH_COST
                # Spiller 2 dash (høyre Ctrl)
                if two_player and event.key == pygame.K_RCTRL and dash_timer2 >= DASH_COOLDOWN and not player_dead2:
                    if fuel2 >= FUEL_DASH_COST:
                        dash_dir2 = pygame.Vector2(0, -1).rotate(angle2)
                        velocity2 = dash_dir2 * DASH_SPEED
                        dash_timer2 = 0
                        dashing2 = True
                        fuel2 -= FUEL_DASH_COST
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                    boost = False

        draw_background(screen, world_pos, stars, planets, elapsed)
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a] and not player_dead:
            angle -= ROTATE_SPEED * dt
        if keys[pygame.K_d] and not player_dead:
            angle += ROTATE_SPEED * dt

        forward = pygame.Vector2(0, -1).rotate(angle)
        if keys[pygame.K_w] and fuel > 0 and not player_dead:
            velocity += forward * THRUST * dt
            fuel = max(0.0, fuel - FUEL_THRUST_DRAIN * dt)

        fire_timer += dt
        if keys[pygame.K_e] and fire_timer >= LASER_FIRE_RATE and not player_dead:
            fire_timer = 0
            spawn_world = world_pos + forward * 45
            laser_vel = velocity + forward * LASER_SPEED
            lasers.append({'pos': spawn_world.copy(), 'vel': laser_vel.copy(), 'life': LASER_LIFETIME})
            if laser_sound:
                laser_sound.play()

        if keys[pygame.K_s] and velocity.length() > 0 and not player_dead:
            brake_force = velocity.normalize() * BRAKE * dt
            if brake_force.length() >= velocity.length():
                velocity = pygame.Vector2(0, 0)
            else:
                velocity -= brake_force

        # Controller support for player 1 (if connected, use second controller if available)
        if len(game_joysticks) > 0:
            # In single player: use first controller. In two player: use second controller if available
            joy_idx = 1 if (two_player and len(game_joysticks) > 1) else 0
            if joy_idx < len(game_joysticks):
                joy1 = game_joysticks[joy_idx]
            # Left stick for rotation (axis 0)
            axis0 = joy1.get_axis(0)
            if abs(axis0) > 0.2:  # Deadzone
                angle += ROTATE_SPEED * axis0 * dt
            
            # Right trigger (button 7) for thrust
            thrust_btn = joy1.get_button(7)
            if thrust_btn and fuel > 0 and not player_dead:
                velocity += forward * THRUST * dt
                fuel = max(0.0, fuel - FUEL_THRUST_DRAIN * dt)
            
            # Left trigger (button 6) for brake
            brake_btn = joy1.get_button(6)
            if brake_btn and velocity.length() > 0 and not player_dead:
                brake_force = velocity.normalize() * BRAKE * dt
                if brake_force.length() >= velocity.length():
                    velocity = pygame.Vector2(0, 0)
                else:
                    velocity -= brake_force
            
            # Right face button (button 1) for fire
            fire_btn = joy1.get_button(1)
            if fire_btn and fire_timer >= LASER_FIRE_RATE and not player_dead:
                fire_timer = 0
                spawn_world = world_pos + forward * 45
                laser_vel = velocity + forward * LASER_SPEED
                lasers.append({'pos': spawn_world.copy(), 'vel': laser_vel.copy(), 'life': LASER_LIFETIME})
                if laser_sound:
                    laser_sound.play()
            
            # Left face button (button 0) for dash
            dash_btn = joy1.get_button(0)
            if dash_btn and dash_timer >= DASH_COOLDOWN and not player_dead:
                if fuel >= FUEL_DASH_COST:
                    dash_dir = pygame.Vector2(0, -1).rotate(angle)
                    velocity = dash_dir * DASH_SPEED
                    dash_timer = 0
                    dashing = True
                    fuel -= FUEL_DASH_COST

        dash_timer += dt
        if dashing and velocity.length() > 0:
            drag = DASH_DRAG_BOOST if boost else DASH_DRAG
            velocity *= max(0.0, 1.0 - drag * dt)
            if velocity.length() <= (BOOST_MAX if boost else MAX_SPEED):
                dashing = False

        if not dashing:
            top_speed = BOOST_MAX if boost else MAX_SPEED
            if velocity.length() > top_speed:
                velocity.scale_to_length(top_speed)

        world_pos += velocity * dt

        # ==================== SPILLER 2 KONTROLLER (keyboard + controller) ====================
        if two_player and player2_active:
            # Keyboard controls
            if keys[pygame.K_LEFT] and not player_dead2:
                angle2 -= ROTATE_SPEED * dt
            if keys[pygame.K_RIGHT] and not player_dead2:
                angle2 += ROTATE_SPEED * dt

            forward2 = pygame.Vector2(0, -1).rotate(angle2)
            if keys[pygame.K_UP] and fuel2 > 0 and not player_dead2:
                velocity2 += forward2 * THRUST * dt
                fuel2 = max(0.0, fuel2 - FUEL_THRUST_DRAIN * dt)

            fire_timer2 += dt
            if keys[pygame.K_PERIOD] and fire_timer2 >= LASER_FIRE_RATE and not player_dead2:
                fire_timer2 = 0
                spawn_world2 = world_pos2 + forward2 * 45
                laser_vel2 = velocity2 + forward2 * LASER_SPEED
                lasers2.append({'pos': spawn_world2.copy(), 'vel': laser_vel2.copy(), 'life': LASER_LIFETIME})
                if laser_sound:
                    laser_sound.play()

            if keys[pygame.K_COMMA] and velocity2.length() > 0 and not player_dead2:
                brake_force2 = velocity2.normalize() * BRAKE * dt
                if brake_force2.length() >= velocity2.length():
                    velocity2 = pygame.Vector2(0, 0)
                else:
                    velocity2 -= brake_force2

            # Controller support for player 2 (use first controller in two-player mode)
            if len(game_joysticks) > 0:
                joy2 = game_joysticks[0]  # First controller for player 2
                # Left stick for rotation (axis 0)
                axis0 = joy2.get_axis(0)
                if abs(axis0) > 0.2:  # Deadzone
                    angle2 += ROTATE_SPEED * axis0 * dt
                
                # Right trigger (axis 5) or button 7 for thrust
                thrust_btn = joy2.get_button(7)  # R2 button
                if thrust_btn and fuel2 > 0 and not player_dead2:
                    velocity2 += forward2 * THRUST * dt
                    fuel2 = max(0.0, fuel2 - FUEL_THRUST_DRAIN * dt)
                
                # Left trigger (axis 4) or button 6 for brake
                brake_btn = joy2.get_button(6)  # L2 button
                if brake_btn and velocity2.length() > 0 and not player_dead2:
                    brake_force2 = velocity2.normalize() * BRAKE * dt
                    if brake_force2.length() >= velocity2.length():
                        velocity2 = pygame.Vector2(0, 0)
                    else:
                        velocity2 -= brake_force2
                
                # Right face button (button 1) for fire
                fire_btn = joy2.get_button(1)
                if fire_btn and fire_timer2 >= LASER_FIRE_RATE and not player_dead2:
                    fire_timer2 = 0
                    spawn_world2 = world_pos2 + forward2 * 45
                    laser_vel2 = velocity2 + forward2 * LASER_SPEED
                    lasers2.append({'pos': spawn_world2.copy(), 'vel': laser_vel2.copy(), 'life': LASER_LIFETIME})
                    if laser_sound:
                        laser_sound.play()
                
                # Left face button (button 0) for dash
                dash_btn = joy2.get_button(0)
                if dash_btn and dash_timer2 >= DASH_COOLDOWN and not player_dead2:
                    if fuel2 >= FUEL_DASH_COST:
                        dash_dir2 = pygame.Vector2(0, -1).rotate(angle2)
                        velocity2 = dash_dir2 * DASH_SPEED
                        dash_timer2 = 0
                        dashing2 = True
                        fuel2 -= FUEL_DASH_COST

            dash_timer2 += dt
            if dashing2 and velocity2.length() > 0:
                drag = DASH_DRAG_BOOST if boost2 else DASH_DRAG
                velocity2 *= max(0.0, 1.0 - drag * dt)
                if velocity2.length() <= (BOOST_MAX if boost2 else MAX_SPEED):
                    dashing2 = False

            if not dashing2:
                top_speed2 = BOOST_MAX if boost2 else MAX_SPEED
                if velocity2.length() > top_speed2:
                    velocity2.scale_to_length(top_speed2)

            world_pos2 += velocity2 * dt

        # Player lasers: update + hit detection on enemies
        alive_lasers = []
        for laser in lasers:
            laser['life'] -= dt
            if laser['life'] <= 0:
                continue
            laser['pos'] += laser['vel'] * dt

            hit_enemy = None
            for enemy in enemies:
                hit_radius = 26 * enemy['scale']
                if laser['pos'].distance_to(enemy['pos']) <= hit_radius:
                    hit_enemy = enemy
                    break

            if hit_enemy is not None:
                hit_enemy['hp'] -= 1
                if hit_enemy['hp'] <= 0:
                    if hit_enemy['boss']:
                        score += 1500
                    else:
                        score += 150
                continue

            rel = laser['pos'] - world_pos
            sx = int(cx + rel.x)
            sy = int(cy + rel.y)
            laser_dir = laser['vel'].normalize() if laser['vel'].length() > 0 else forward
            tail = pygame.Vector2(sx, sy) - laser_dir * 18
            alpha = min(1.0, laser['life'] / LASER_LIFETIME)
            pygame.draw.line(screen, (0, int(200 * alpha), 0), (sx, sy), (int(tail.x), int(tail.y)), 3)
            pygame.draw.line(screen, (int(200 * alpha), 255, int(200 * alpha)), (sx, sy), (int(tail.x + laser_dir.x * 6), int(tail.y + laser_dir.y * 6)), 1)
            alive_lasers.append(laser)
        lasers = alive_lasers

        # ==================== SPILLER 2 LASERE ====================
        if two_player and player2_active:
            alive_lasers2 = []
            for laser in lasers2:
                laser['life'] -= dt
                if laser['life'] <= 0:
                    continue
                laser['pos'] += laser['vel'] * dt

                hit_enemy = None
                for enemy in enemies:
                    hit_radius = 26 * enemy['scale']
                    if laser['pos'].distance_to(enemy['pos']) <= hit_radius:
                        hit_enemy = enemy
                        break

                if hit_enemy is not None:
                    hit_enemy['hp'] -= 1
                    if hit_enemy['hp'] <= 0:
                        if hit_enemy['boss']:
                            score += 1500
                        else:
                            score += 150
                    continue

                rel = laser['pos'] - world_pos2
                sx = int(cx + rel.x)
                sy = int(cy + rel.y)
                laser_dir = laser['vel'].normalize() if laser['vel'].length() > 0 else forward2
                tail = pygame.Vector2(sx, sy) - laser_dir * 18
                alpha = min(1.0, laser['life'] / LASER_LIFETIME)
                pygame.draw.line(screen, (0, int(200 * alpha), 0), (sx, sy), (int(tail.x), int(tail.y)), 3)
                pygame.draw.line(screen, (int(200 * alpha), 255, int(200 * alpha)), (sx, sy), (int(tail.x + laser_dir.x * 6), int(tail.y + laser_dir.y * 6)), 1)
                alive_lasers2.append(laser)
            lasers2 = alive_lasers2

        # Remove dead enemies before movement and next-wave check
        enemies = [e for e in enemies if e['hp'] > 0]

        # Enemies: movement, shooting, drawing
        alive_enemy_lasers = []
        for enemy in enemies:
            to_player = world_pos - enemy['pos']
            dist = to_player.length()
            if dist > 0:
                to_player_dir = to_player.normalize()
                desired = to_player_dir * enemy['speed']
                # Ekstra "pull" mot spiller for tydelig jagende fiender.
                enemy['vel'] += to_player_dir * (220 * dt)
                enemy['vel'] = enemy['vel'].lerp(desired, min(1.0, 4.2 * dt))
                enemy['pos'] += enemy['vel'] * dt
                if enemy['vel'].length() > 0.1:
                    enemy['angle'] = math.degrees(math.atan2(enemy['vel'].y, enemy['vel'].x)) + 90

            enemy['fire_cd'] -= dt
            if enemy['fire_cd'] <= 0 and dist < 1700:
                enemy['fire_cd'] = enemy['fire_rate']
                if dist > 0:
                    shoot_dir = to_player.normalize()
                else:
                    shoot_dir = pygame.Vector2(0, 1)

                spread_list = [0]
                if enemy['boss']:
                    spread_list = [-8, 0, 8]

                for spread in spread_list:
                    sdir = shoot_dir.rotate(spread)
                    enemy_lasers.append({
                        'pos': enemy['pos'] + sdir * (30 * enemy['scale']),
                        'vel': sdir * ENEMY_LASER_SPEED,
                        'life': ENEMY_LASER_LIFETIME,
                    })

            enemy_rel = enemy['pos'] - world_pos
            esx = int(cx + enemy_rel.x)
            esy = int(cy + enemy_rel.y)
            if -380 < esx < screen.get_width() + 380 and -380 < esy < screen.get_height() + 380:
                draw_ship(screen, enemy_ship_id, (esx, esy), enemy['angle'], enemy_color, scale=enemy['scale'])
                if enemy['boss']:
                    hp_ratio = max(0.0, enemy['hp'] / enemy['max_hp'])
                    bar_w = 130
                    pygame.draw.rect(screen, (40, 10, 10), (esx - bar_w // 2, esy - 95, bar_w, 9))
                    pygame.draw.rect(screen, (220, 50, 50), (esx - bar_w // 2, esy - 95, int(bar_w * hp_ratio), 9))

        # Enemy lasers update + collision with player ship in center
        for el in enemy_lasers:
            el['life'] -= dt
            if el['life'] <= 0:
                continue
            el['pos'] += el['vel'] * dt

            if el['pos'].distance_to(world_pos) <= 42:
                if not player_dead:
                    player_hits += 1
                    if player_hits >= 3:
                        player_dead = True
                        death_timer = 1.0
                continue

            # ==================== SPILLER 2 KOLLISJON ====================
            if two_player and player2_active and el['pos'].distance_to(world_pos2) <= 42:
                if not player_dead2:
                    player_hits2 += 1
                    if player_hits2 >= 3:
                        player_dead2 = True
                        death_timer = 1.0
                continue

            rel = el['pos'] - world_pos
            sx = int(cx + rel.x)
            sy = int(cy + rel.y)
            edir = el['vel'].normalize() if el['vel'].length() > 0 else pygame.Vector2(0, 1)
            tail = pygame.Vector2(sx, sy) - edir * 16
            pygame.draw.line(screen, (255, 45, 45), (sx, sy), (int(tail.x), int(tail.y)), 3)
            pygame.draw.line(screen, (255, 180, 180), (sx, sy), (int(tail.x + edir.x * 4), int(tail.y + edir.y * 4)), 1)
            alive_enemy_lasers.append(el)
        enemy_lasers = alive_enemy_lasers

        # Space station spawning (tilfeldig, men ofte)
        station_spawn_timer += dt
        if station_spawn_timer >= STATION_SPAWN_INTERVAL:
            station_spawn_timer = 0
            if len(stations) < 8 and random.random() < 0.8:
                spawn_angle = random.uniform(0, 360)
                spawn_dist = random.uniform(700, 1900)
                stations.append({'pos': world_pos + pygame.Vector2(0, -1).rotate(spawn_angle) * spawn_dist})

        stations = [s for s in stations if s['pos'].distance_to(world_pos) < 7000]
        near_station = False
        for station in stations:
            rel = station['pos'] - world_pos
            sx = int(cx + rel.x)
            sy = int(cy + rel.y)
            if -180 < sx < screen.get_width() + 180 and -180 < sy < screen.get_height() + 180:
                if STATION_SPRITE is not None:
                    glow = 58
                    pygame.draw.circle(screen, (60, 130, 170), (sx, sy), glow, 1)
                    pygame.draw.circle(screen, (32, 72, 102), (sx, sy), glow - 12, 1)
                    station_rect = STATION_SPRITE.get_rect(center=(sx, sy))
                    screen.blit(STATION_SPRITE, station_rect)
                else:
                    pygame.draw.circle(screen, (90, 180, 220), (sx, sy), 34, 2)
                    pygame.draw.circle(screen, (40, 90, 120), (sx, sy), 22, 2)
                    tag = get_font(14).render("F", True, "#9de7ff")
                    screen.blit(tag, tag.get_rect(center=(sx, sy - 1)))
            if station['pos'].distance_to(world_pos) <= STATION_INTERACT_RADIUS:
                near_station = True

        if near_station:
            fill_prompt = pygame.font.SysFont("arial", 54, bold=True).render("PRESS Q TO FILL FUEL", True, (255, 240, 150))
            fill_prompt_shadow = pygame.font.SysFont("arial", 54, bold=True).render("PRESS Q TO FILL FUEL", True, (15, 20, 30))
            prompt_rect = fill_prompt.get_rect(center=(cx, 240))
            screen.blit(fill_prompt_shadow, (prompt_rect.x + 4, prompt_rect.y + 4))
            screen.blit(fill_prompt, prompt_rect)

        if near_station and keys[pygame.K_q]:
            fuel = min(config.FUEL_MAX, fuel + FUEL_REFILL_RATE * dt)

        # ==================== SPILLER 2 FUEL STASJON ====================
        if two_player and player2_active:
            near_station2 = False
            for station in stations:
                if station['pos'].distance_to(world_pos2) <= STATION_INTERACT_RADIUS:
                    near_station2 = True
                    break
            
            if near_station2 and keys[pygame.K_SLASH]:  # / for player 2
                fuel2 = min(config.FUEL_MAX, fuel2 + FUEL_REFILL_RATE * dt)

        # Komet spawning
        comet_spawn_timer += dt
        if comet_spawn_timer >= COMET_SPAWN_INTERVAL:
            comet_spawn_timer = 0
            if len(comets) < COMET_COUNT and random.random() < 0.7:
                spawn_angle = random.uniform(0, 360)
                spawn_dist = random.uniform(800, 2000)
                comets.append({
                    'pos': world_pos + pygame.Vector2(0, -1).rotate(spawn_angle) * spawn_dist,
                    'vel': pygame.Vector2(0, 0),
                })

        # Fjern kometer som er for langt unna
        comets = [c for c in comets if c['pos'].distance_to(world_pos) < 7000]

        # Tegn og oppdater kometer
        for comet in comets:
            # Beveg komet mot spiller
            to_player = world_pos - comet['pos']
            if to_player.length() > 0:
                comet['vel'] = to_player.normalize() * COMET_SPEED
            comet['pos'] += comet['vel'] * dt

            rel = comet['pos'] - world_pos
            sx = int(cx + rel.x)
            sy = int(cx + rel.y)

            if -100 < sx < screen.get_width() + 100 and -100 < sy < screen.get_height() + 100:
                if COMET_SPRITE is not None:
                    comet_rect = COMET_SPRITE.get_rect(center=(sx, sy))
                    screen.blit(COMET_SPRITE, comet_rect)
                else:
                    pygame.draw.circle(screen, (180, 100, 50), (sx, sy), COMET_SIZE, 2)
                    pygame.draw.circle(screen, (255, 150, 80), (sx, sy), COMET_SIZE - 8, 1)

            # Kollisjonssjekk med spiller
            if not player_dead and comet['pos'].distance_to(world_pos) <= COMET_SIZE + 30:
                score += COMET_SCORE_PENALTY
                comets.remove(comet)
                continue

            # Kollisjonssjekk med spiller 2
            if two_player and player2_active and not player_dead2 and comet['pos'].distance_to(world_pos2) <= COMET_SIZE + 30:
                score += COMET_SCORE_PENALTY
                comets.remove(comet)
                continue

        # Planet/kollisjon
        for pl in planets:
            # Sjekk kollisjon med spiller 1
            if not player_dead and pl['world'].distance_to(world_pos) <= pl['radius'] + 30:
                score += config.SCORE_PLANET_HIT
            # Sjekk kollisjon med spiller 2
            if two_player and player2_active and not player_dead2 and pl['world'].distance_to(world_pos2) <= pl['radius'] + 30:
                score += config.SCORE_PLANET_HIT

        # Wave progression
        if len(enemies) == 0 and wave < MAX_WAVE and not between_waves:
            between_waves = True
            wave_countdown = 15.0
            enemy_lasers = []

        if between_waves:
            wave_countdown -= dt
            if wave_countdown <= 0:
                between_waves = False
                wave += 1
                enemies = spawn_wave(wave)
                wave_banner_timer = 2.0

        # Player ship farge etter skade: normal -> orange -> red -> death
        ship_color = player_color
        if player_hits == 1:
            ship_color = (255, 165, 40)
        elif player_hits >= 2:
            ship_color = (235, 70, 70)
        draw_ship(screen, selected_ship, screen_center, angle, ship_color, scale=1.35)

        # ==================== SPILLER 2 SKIP ====================
        if two_player and player2_active:
            # Spiller 2 posisjon (offset fra spiller 1)
            screen_center2 = pygame.Vector2(cx - 80, cy + 80)
            ship_color2 = player_color2
            if player_hits2 == 1:
                ship_color2 = (255, 165, 40)
            elif player_hits2 >= 2:
                ship_color2 = (235, 70, 70)
            draw_ship(screen, selected_ship2, screen_center2, angle2, ship_color2, scale=1.35)

        # Bottom-right score UI
        ui_w = 320
        ui_h = 300
        ui_x = screen.get_width() - ui_w - 14
        ui_y = screen.get_height() - ui_h - 14
        ui_panel = pygame.Surface((ui_w, ui_h), pygame.SRCALPHA)
        ui_panel.fill((8, 12, 24, 190))
        screen.blit(ui_panel, (ui_x, ui_y))
        pygame.draw.rect(screen, (60, 80, 120), (ui_x, ui_y, ui_w, ui_h), 2)

        info_lines = [
            ("FUEL", f"{int(fuel)}%", "#9de7ff"),
        ]
        y = ui_y + 26
        for title, value, color in info_lines:
            t = get_font(18).render(title.upper(), True, "#7e8ba7")
            v = get_font(28).render(str(value).upper(), True, color)
            screen.blit(t, (ui_x + 24, y))
            screen.blit(v, (ui_x + 24, y + 24))
            y += 46

        # Tydelig score/enemies nederst til høyre med lesbar standardfont.
        ui_font_small = pygame.font.SysFont("arial", 18, bold=True)
        ui_font_big = pygame.font.SysFont("arial", 34, bold=True)
        points_label = ui_font_small.render("POINTS", True, (170, 190, 220))
        points_value = ui_font_big.render(str(score), True, (215, 252, 212))
        enemies_label = ui_font_small.render("ENEMIES LEFT", True, (170, 190, 220))
        enemies_value = ui_font_big.render(str(len(enemies)), True, (240, 144, 144))
        screen.blit(points_label, (ui_x + 24, ui_y + ui_h - 176))
        screen.blit(points_value, (ui_x + 24, ui_y + ui_h - 152))
        screen.blit(enemies_label, (ui_x + 170, ui_y + ui_h - 176))
        screen.blit(enemies_value, (ui_x + 170, ui_y + ui_h - 152))

        fuel_w = ui_w - 48
        pygame.draw.rect(screen, (35, 50, 70), (ui_x + 24, ui_y + ui_h - 54, fuel_w, 14))
        pygame.draw.rect(screen, (80, 210, 255), (ui_x + 24, ui_y + ui_h - 54, int(fuel_w * (fuel / config.FUEL_MAX)), 14))

        # Helsebar (3 treff): grønn -> orange -> rød -> tom
        hp_left = max(0, 3 - player_hits)
        hp_ratio = hp_left / 3
        hp_color = (80, 220, 110)
        if hp_left == 2:
            hp_color = (255, 165, 40)
        elif hp_left == 1:
            hp_color = (235, 70, 70)
        hp_bg_y = ui_y + ui_h - 78
        hp_w = ui_w - 48
        hp_title = get_font(14).render("HULL", True, "#9ab58f")
        screen.blit(hp_title, (ui_x + 24, hp_bg_y - 18))
        pygame.draw.rect(screen, (35, 50, 70), (ui_x + 24, hp_bg_y, hp_w, 12))
        pygame.draw.rect(screen, hp_color, (ui_x + 24, hp_bg_y, int(hp_w * hp_ratio), 12))

        # ==================== SPILLER 2 UI ====================
        if two_player and player2_active:
            # Spiller 2 fuel bar (venstre side)
            ui_x2 = 14
            ui_y2 = screen.get_height() - ui_h - 14
            ui_panel2 = pygame.Surface((ui_w, ui_h), pygame.SRCALPHA)
            ui_panel2.fill((8, 12, 24, 190))
            screen.blit(ui_panel2, (ui_x2, ui_y2))
            pygame.draw.rect(screen, (60, 80, 120), (ui_x2, ui_y2, ui_w, ui_h), 2)

            info_lines2 = [
                ("FUEL", f"{int(fuel2)}%", "#9de7ff"),
            ]
            y2 = ui_y2 + 26
            for title, value, color in info_lines2:
                t2 = get_font(18).render(title.upper(), True, "#7e8ba7")
                v2 = get_font(28).render(str(value).upper(), True, color)
                screen.blit(t2, (ui_x2 + 24, y2))
                screen.blit(v2, (ui_x2 + 24, y2 + 24))
                y2 += 46

            # Spiller 2 helsebar
            hp_left2 = max(0, 3 - player_hits2)
            hp_ratio2 = hp_left2 / 3
            hp_color2 = (80, 220, 110)
            if hp_left2 == 2:
                hp_color2 = (255, 165, 40)
            elif hp_left2 == 1:
                hp_color2 = (235, 70, 70)
            hp_bg_y2 = ui_y2 + ui_h - 78
            hp_title2 = get_font(14).render("HULL", True, "#9ab58f")
            screen.blit(hp_title2, (ui_x2 + 24, hp_bg_y2 - 18))
            pygame.draw.rect(screen, (35, 50, 70), (ui_x2 + 24, hp_bg_y2, hp_w, 12))
            pygame.draw.rect(screen, hp_color2, (ui_x2 + 24, hp_bg_y2, int(hp_w * hp_ratio2), 12))

            # Spiller 2 label
            p2_label = get_font(16).render("PLAYER 2", True, "#9de7ff")
            screen.blit(p2_label, (ui_x2 + 24, ui_y2 + ui_h - 34))

        if between_waves:
            next_wave = min(MAX_WAVE, wave + 1)
            c = int(math.ceil(max(0.0, wave_countdown)))
            next_txt = get_font(16).render(f"NEXT: {next_wave} IN {c}S", True, "#e7e7e7")
            screen.blit(next_txt, (ui_x + 24, ui_y + ui_h - 88))

            # Tydelig stor nedtelling mellom waves.
            timer_panel = pygame.Surface((420, 130), pygame.SRCALPHA)
            timer_panel.fill((10, 14, 28, 190))
            panel_rect = timer_panel.get_rect(center=(cx, 140))
            screen.blit(timer_panel, panel_rect)
            pygame.draw.rect(screen, (120, 135, 190), panel_rect, 2)
            timer_label = pygame.font.SysFont("arial", 24, bold=True).render(f"NEXT WAVE {next_wave} IN", True, (215, 223, 238))
            timer_value = pygame.font.SysFont("arial", 62, bold=True).render(f"{c} S", True, (255, 230, 152))
            screen.blit(timer_label, timer_label.get_rect(center=(cx, 112)))
            screen.blit(timer_value, timer_value.get_rect(center=(cx, 164)))

            # Visuell progress-bar for 15s nedtelling.
            t_ratio = max(0.0, min(1.0, wave_countdown / 15.0))
            bar_w = 360
            bar_h = 14
            bar_x = cx - bar_w // 2
            bar_y = 188
            pygame.draw.rect(screen, (28, 38, 56), (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(screen, (255, 210, 110), (bar_x, bar_y, int(bar_w * t_ratio), bar_h))

        if wave % 5 == 0 and len(enemies) > 0:
            boss_txt = get_font(18).render("BOSS WAVE", True, "#ff6a6a")
            screen.blit(boss_txt, (ui_x + 24, ui_y + ui_h - 34))

        if wave_banner_timer > 0:
            wave_title = f"WAVE {to_roman(wave)}"
            if wave % 5 == 0:
                wave_title += "  -  BOSS"
            banner = get_font(34).render(wave_title, True, "#fcecc2")
            screen.blit(banner, banner.get_rect(center=(cx, 70)))
            wave_banner_timer -= dt

        if player_dead:
            over = get_font(50).render("GAME OVER", True, "#ff6565")
            screen.blit(over, over.get_rect(center=(cx, cy - 20)))
            sub = get_font(20).render("RETURNING TO MAIN MENU...", True, "#f0f0f0")
            screen.blit(sub, sub.get_rect(center=(cx, cy + 26)))
            death_timer -= dt
            if death_timer <= 0:
                main_menu()

        if wave >= MAX_WAVE and len(enemies) == 0:
            win = get_font(44).render("YOU CLEARED ALL 200 WAVES", True, "#9dffbe")
            screen.blit(win, win.get_rect(center=(cx, cy - 20)))

        if keys[pygame.K_ESCAPE]:
            main_menu()

        pygame.display.flip()

        dt = clock.tick(config.FPS) / 1000
        elapsed += dt

    pygame.quit()
    sys.exit()

main_menu()