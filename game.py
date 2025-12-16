import pygame
import os
import random
import math


pygame.init()


# --- Window setup ---
WIDTH, HEIGHT = 1280, 720  # Use a more common window size for testing
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Katinuko žvejyba")


clock = pygame.time.Clock()


# --- Font setup ---
pygame.font.init()
title_font = pygame.font.SysFont('Arial', 72, bold=True)
title_surface = title_font.render("Katinuko žvejyba", True, (255, 255, 255))
title_rect = title_surface.get_rect(center=(WIDTH // 2, 60))


# --- Load assets ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images")

# define paths FIRST
background_path = os.path.join(IMAGES_DIR, "ezeras.png")
sprite_sheet_path = os.path.join(IMAGES_DIR, "valtis_anim.png")
varna_sheet_path = os.path.join(IMAGES_DIR, "varna_Sheet.png")
zuvys_sheet_path = os.path.join(IMAGES_DIR, "zuvys_sheet.png")
press_e_path = os.path.join(IMAGES_DIR, "press_e_Sheet.png")
uzmesti_path = os.path.join(IMAGES_DIR, "uzmesti_Sheet.png")
dugnas_path = os.path.join(IMAGES_DIR, "dugnas.png")

# load sheets safely (convert_alpha) after paths exist
try:
    sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
except Exception:
    sprite_sheet = None

try:
    varna_sheet = pygame.image.load(varna_sheet_path).convert_alpha()
except Exception:
    varna_sheet = None

try:
    zuvys_sheet = pygame.image.load(zuvys_sheet_path).convert_alpha()
except Exception:
    zuvys_sheet = None

# new sheets for prompt/cast
press_e_path = os.path.join(IMAGES_DIR, "press_e_Sheet.png")
uzmesti_path = os.path.join(IMAGES_DIR, "uzmesti_Sheet.png")
# new: bottom/dugnas scene
dugnas_path = os.path.join(IMAGES_DIR, "dugnas.png")


# safe image loads: fallback to simple placeholder instead of crashing
def safe_load(path, convert_alpha=False, size=None, fill_color=(255, 0, 255, 128)):
    try:
        img = pygame.image.load(path)
        img = img.convert_alpha() if convert_alpha else img.convert()
        if size is not None:
            img = pygame.transform.scale(img, size)
        return img
    except Exception:
        # placeholder surface (visible magenta) so you can spot missing art
        w, h = size if size else (128, 128)
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        pygame.draw.rect(surf, (255, 0, 255), surf.get_rect(), 3)
        return surf

background = safe_load(background_path, convert_alpha=False, size=(WIDTH, HEIGHT))
bg_width, bg_height = background.get_size()

# load dugnas scene (scaled to window)
dugnas = safe_load(dugnas_path, convert_alpha=False, size=(WIDTH, HEIGHT))

# play looping background music from sounds/littlefishes.mp3 (safe if missing)
SOUNDS_DIR = os.path.join(BASE_DIR, "sounds")
music_path = os.path.join(SOUNDS_DIR, "littlefishes.mp3")
try:
    if os.path.exists(music_path):
        try:
            pygame.mixer.init()
        except Exception:
            pass
        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)  # loop indefinitely
        except Exception:
            # ignore load/play errors
            pass
except Exception:
    pass

# load hurt sound for shark hits (safe)
hurt_sound = None
try:
    hurt_path = os.path.join(SOUNDS_DIR, "hurt.mp3")
    if os.path.exists(hurt_path):
        try:
            # ensure mixer initialized
            pygame.mixer.init()
        except Exception:
            pass
        try:
            hurt_sound = pygame.mixer.Sound(hurt_path)
            hurt_sound.set_volume(0.7)
        except Exception:
            hurt_sound = None
except Exception:
    hurt_sound = None

# load reelin sound for catching fish (safe)
reelin_sound = None
try:
    reelin_path = os.path.join(SOUNDS_DIR, "reelin.mp3")
    if os.path.exists(reelin_path):
        try:
            pygame.mixer.init()
        except Exception:
            pass
        try:
            reelin_sound = pygame.mixer.Sound(reelin_path)
            reelin_sound.set_volume(0.7)
        except Exception:
            reelin_sound = None
except Exception:
    reelin_sound = None

# load coin sound
coin_sound = None
try:
    coin_path = os.path.join(SOUNDS_DIR, "coins.mp3")
    if os.path.exists(coin_path):
        try:
            pygame.mixer.init()
        except Exception:
            pass
        try:
            coin_sound = pygame.mixer.Sound(coin_path)
            coin_sound.set_volume(0.7)
        except Exception:
            coin_sound = None
except Exception:
    coin_sound = None

# --- Coin (pinigas) sprite: 128x16 (8 frames horizontally, each 16x16) ---
coin_frames = []
try:
    coin_sheet = pygame.image.load(os.path.join(IMAGES_DIR, "pinigas.png")).convert_alpha()
    frame_w, frame_h, frames_count = 16, 16, 8
    COIN_SCALE = 2  # padidinimas
    for i in range(frames_count):
        sub = coin_sheet.subsurface((i * frame_w, 0, frame_w, frame_h)).copy()
        sub = pygame.transform.scale(sub, (frame_w * COIN_SCALE, frame_h * COIN_SCALE))
        coin_frames.append(sub)
except Exception:
    # fallback paprastas apskritimas
    ph = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.circle(ph, (255, 220, 0), (16, 16), 12)
    pygame.draw.circle(ph, (200, 160, 0), (16, 16), 12, 3)
    coin_frames = [ph]

# coins state
coins = []  # each: {"x","y","rect","frame_idx","frame_tick"}
coins_collected = 0


# --- Animation setup ---
FRAME_WIDTH = 128
FRAME_HEIGHT = 128
NUM_FRAMES = 5
SCALE = 2


frames = []
for i in range(NUM_FRAMES):
   if sprite_sheet:
       sheet_w = sprite_sheet.get_width()
       # ensure the requested subsurface is inside the sprite sheet
       if (i + 1) * FRAME_WIDTH <= sheet_w:
           frame = sprite_sheet.subsurface((i * FRAME_WIDTH, 0, FRAME_WIDTH, FRAME_HEIGHT))
       else:
           # fallback: create a placeholder for missing frames
           frame = pygame.Surface((FRAME_WIDTH, FRAME_HEIGHT), pygame.SRCALPHA)
           pygame.draw.rect(frame, (255, 0, 255), frame.get_rect(), 2)
   else:
       frame = pygame.Surface((FRAME_WIDTH, FRAME_HEIGHT), pygame.SRCALPHA)
       pygame.draw.rect(frame, (255, 0, 255), frame.get_rect(), 2)

   frame = pygame.transform.scale(frame, (FRAME_WIDTH * SCALE, FRAME_HEIGHT * SCALE))
   frames.append(frame)


# --- Player setup ---
cat_x = (WIDTH - FRAME_WIDTH * SCALE) // 2
cat_y = (HEIGHT - FRAME_HEIGHT * SCALE) // 2 + 100  # Move 100 pixels lower


speed = 8
current_frame = 0
facing_left = False
moving = False


# --- World scrolling ---
scroll_x = 0
running = True


# --- Margins for scrolling ---
LEFT_MARGIN = WIDTH // 3
RIGHT_MARGIN = WIDTH - WIDTH // 3 - FRAME_WIDTH * SCALE


# --- Varna animals setup ---
VARNA_FRAME_WIDTH = 64
VARNA_FRAME_HEIGHT = 64
VARNA_NUM_FRAMES = 5
VARNA_SCALE = 2


# Varna frames (safe)
varna_frames = []
for i in range(VARNA_NUM_FRAMES):
   if varna_sheet:
       sheet_w = varna_sheet.get_width()
       if (i + 1) * VARNA_FRAME_WIDTH <= sheet_w:
           frame = varna_sheet.subsurface((i * VARNA_FRAME_WIDTH, 0, VARNA_FRAME_WIDTH, VARNA_FRAME_HEIGHT))
       else:
           frame = pygame.Surface((VARNA_FRAME_WIDTH, VARNA_FRAME_HEIGHT), pygame.SRCALPHA)
           pygame.draw.rect(frame, (255, 0, 255), frame.get_rect(), 2)
   else:
       frame = pygame.Surface((VARNA_FRAME_WIDTH, VARNA_FRAME_HEIGHT), pygame.SRCALPHA)
       pygame.draw.rect(frame, (255, 0, 255), frame.get_rect(), 2)
   frame = pygame.transform.scale(frame, (VARNA_FRAME_WIDTH * VARNA_SCALE, VARNA_FRAME_HEIGHT * VARNA_SCALE))
   varna_frames.append(frame)


# Create moving varna animals
varna_animals = []
for pos in [(300, 100), (700, 150), (1100, 80), (1600, 120)]:
   varna_animals.append({
       "x": pos[0],
       "y": pos[1],
       "dx": random.choice([-1, 1]) * random.uniform(0.5, 1.5),
       "dy": random.choice([-1, 1]) * random.uniform(0.2, 0.7)
   })


varna_anim_frame = 0


# --- Zuvys (fish) setup ---
ZUVYS_FRAME_WIDTH = 64
ZUVYS_FRAME_HEIGHT = 64
ZUVYS_NUM_FRAMES = 4
ZUVYS_SCALE = 2

# new: underwater Zuvis_A scale and blizgės (player) scale
ZUVA_SCALE = 3     # padidina povandenines žuvis
BLIZGE_SCALE = 0.5 # sumažina blizgės paveikslėlį (tweak: 0.2..0.8)


# Zuvys frames (safe)
zuvys_frames = []
for i in range(ZUVYS_NUM_FRAMES):
   if zuvys_sheet:
       sheet_w = zuvys_sheet.get_width()
       if (i + 1) * ZUVYS_FRAME_WIDTH <= sheet_w:
           frame = zuvys_sheet.subsurface((i * ZUVYS_FRAME_WIDTH, 0, ZUVYS_FRAME_WIDTH, ZUVYS_FRAME_HEIGHT))
       else:
           frame = pygame.Surface((ZUVYS_FRAME_WIDTH, ZUVYS_FRAME_HEIGHT), pygame.SRCALPHA)
           pygame.draw.rect(frame, (255, 0, 255), frame.get_rect(), 2)
   else:
       frame = pygame.Surface((ZUVYS_FRAME_WIDTH, ZUVYS_FRAME_HEIGHT), pygame.SRCALPHA)
       pygame.draw.rect(frame, (255, 0, 255), frame.get_rect(), 2)
   frame = pygame.transform.scale(frame, (ZUVYS_FRAME_WIDTH * ZUVYS_SCALE, ZUVYS_FRAME_HEIGHT * ZUVYS_SCALE))
   zuvys_frames.append(frame)


# Positions for fish near the middle of the scene
zuvys_positions = [
   (WIDTH // 2 - 100, HEIGHT // 2 + 150),
]

zuvys_anim_frame = 0

# --- track fishing spots state ---
disabled_spots = set()            # spots that were fully fished out
current_fishing_spot = None       # the spot we're currently fishing (entered underwater from)
last_spawned_count = 0            # how many fish were spawned for the current spot


# --- Press-E / Uzmesti animation setup ---
# Adjust these sizes if your sheets use different frame sizes
PRESS_E_FRAME_WIDTH = 64
PRESS_E_FRAME_HEIGHT = 64
PRESS_E_NUM_FRAMES = 4
PRESS_E_SCALE = 2

UZM_FRAME_WIDTH = 128
UZM_FRAME_HEIGHT = 128
UZM_NUM_FRAMES = 6
UZM_SCALE = 2

# load press-e sheet (fallback placeholder if missing)
try:
    press_e_sheet = pygame.image.load(press_e_path).convert_alpha()
except Exception:
    press_e_sheet = pygame.Surface((PRESS_E_FRAME_WIDTH, PRESS_E_FRAME_HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(press_e_sheet, (255, 255, 0), press_e_sheet.get_rect(), 2)

press_e_frames = []
for i in range(PRESS_E_NUM_FRAMES):
    try:
        frame = press_e_sheet.subsurface((i * PRESS_E_FRAME_WIDTH, 0, PRESS_E_FRAME_WIDTH, PRESS_E_FRAME_HEIGHT))
    except Exception:
        frame = press_e_sheet.copy()
    frame = pygame.transform.scale(frame, (PRESS_E_FRAME_WIDTH * PRESS_E_SCALE, PRESS_E_FRAME_HEIGHT * PRESS_E_SCALE))
    press_e_frames.append(frame)

# load uzmesti (cast) sheet (fallback placeholder if missing)
try:
    uzmesti_sheet = pygame.image.load(uzmesti_path).convert_alpha()
except Exception:
    uzmesti_sheet = pygame.Surface((UZM_FRAME_WIDTH, UZM_FRAME_HEIGHT), pygame.SRCALPHA)
    pygame.draw.circle(uzmesti_sheet, (0, 255, 0), (UZM_FRAME_WIDTH//2, UZM_FRAME_HEIGHT//2), UZM_FRAME_WIDTH//3, 3)

uzmesti_frames = []
for i in range(UZM_NUM_FRAMES):
    try:
        frame = uzmesti_sheet.subsurface((i * UZM_FRAME_WIDTH, 0, UZM_FRAME_WIDTH, UZM_FRAME_HEIGHT))
    except Exception:
        frame = uzmesti_sheet.copy()
    frame = pygame.transform.scale(frame, (UZM_FRAME_WIDTH * UZM_SCALE, UZM_FRAME_HEIGHT * UZM_SCALE))
    uzmesti_frames.append(frame)

# animation state
press_e_anim_frame = 0.0
uzmesti_anim_frame = 0.0
casting = False
# show the dugnas scene after cast finishes
show_dugnas = False

# --- Underwater mini-game assets & state ---
zuvis_a_path = os.path.join(IMAGES_DIR, "Zuvis_A.png")

# Try load Zuvis_A as a sprite sheet (fall back to single image)
try:
    zuvis_a_sheet = pygame.image.load(zuvis_a_path).convert_alpha()
except Exception:
    zuvis_a_sheet = None

# build frames from Zuvis_A sprite sheet (8 frames)
zuvis_a_frames = []
if zuvis_a_sheet:
    SHEET_FRAMES = 8
    sheet_w = zuvis_a_sheet.get_width()
    sheet_h = zuvis_a_sheet.get_height()
    # compute per-frame size (sheet is 256x16 -> frame_w=32, frame_h=16)
    frame_w = max(1, sheet_w // SHEET_FRAMES)
    frame_h = sheet_h

    for i in range(SHEET_FRAMES):
        x = i * frame_w
        # safety: ensure subsurface inside sheet
        if x + frame_w <= sheet_w and frame_h <= sheet_h:
            sub = zuvis_a_sheet.subsurface((x, 0, frame_w, frame_h)).copy()
            # detect magenta placeholder (255,0,255) by sampling center pixel and skip it
            try:
                px = sub.get_at((frame_w // 2, frame_h // 2))
                if (px.r, px.g, px.b) == (255, 0, 255):
                    continue
            except Exception:
                pass
            # scale underwater fish using ZUVA_SCALE (separate from surface fish scale)
            sub = pygame.transform.scale(sub, (int(frame_w * ZUVA_SCALE), int(frame_h * ZUVA_SCALE)))
            zuvis_a_frames.append(sub)

# fallback single image if extraction failed
if not zuvis_a_frames:
    zuvis_a_img = safe_load(zuvis_a_path, convert_alpha=True, size=(int(ZUVYS_FRAME_WIDTH * ZUVA_SCALE), int(ZUVYS_FRAME_HEIGHT * ZUVA_SCALE)))
else:
    zuvis_a_img = zuvis_a_frames[0]

underwater_fish = []   # list of dicts: {x,y,dx,rect,frame_idx,frame_tick}
caught_count = 0

# load underwater player sprite (blizge.png)
blizge_path = os.path.join(IMAGES_DIR, "blizge.png")
blizge_img = safe_load(
    blizge_path,
    convert_alpha=True,
    size=(
        int(ZUVYS_FRAME_WIDTH * ZUVA_SCALE * BLIZGE_SCALE),
        int(ZUVYS_FRAME_HEIGHT * ZUVA_SCALE * BLIZGE_SCALE),
    ),
)

# underwater player physics state (initialized when entering underwater)
uw_player_x = WIDTH // 2
uw_player_y = 80
uw_player_vy = 0.0
uw_scroll_x = 0  # camera offset for underwater world (fix NameError when entering underwater)
UW_SPEED = 3.0
GRAVITY = 0.35

# hook position where the cast ended (set when casting finishes)
cast_hook_x = None
cast_hook_y = None

def spawn_underwater_fish(n=6):
    global last_spawned_count
    underwater_fish.clear()
    last_spawned_count = n
    for i in range(n):
        x = random.randint(100, WIDTH - 100)
        y = random.randint(HEIGHT//2 + 20, HEIGHT - 120)
        dx = random.choice([-1, 1]) * random.uniform(1.0, 2.2)
        rect = pygame.Rect(x, y, zuvis_a_img.get_width(), zuvis_a_img.get_height())
        underwater_fish.append({"x": x, "y": y, "dx": dx, "rect": rect, "frame_idx": 0, "frame_tick": 0, "caught": False})


# --- Shark (riklys) assets & state ---
RIKLYS_SHEET_A_PATH = os.path.join(IMAGES_DIR, "riklys_a.png")  # idle/swim sheet (256x16, 8 frames)
RIKLYS_SHEET_B_PATH = os.path.join(IMAGES_DIR, "riklys_b.png")  # attack sheet (256x16, 8 frames)
RIKLYS_SHEET_FRAMES = 8
RIKLYS_SCALE = int(ZUVA_SCALE) if 'ZUVA_SCALE' in globals() else 3

def build_sheet_frames(path, frames_count=8, scale=RIKLYS_SCALE):
    frames = []
    try:
        sheet = pygame.image.load(path).convert_alpha()
        sheet_w, sheet_h = sheet.get_width(), sheet.get_height()
        frame_w = max(1, sheet_w // frames_count)
        for i in range(frames_count):
            x = i * frame_w
            if x + frame_w <= sheet_w:
                sub = sheet.subsurface((x, 0, frame_w, sheet_h)).copy()
                # skip magenta placeholder frames if detected
                try:
                    px = sub.get_at((frame_w // 2, sheet_h // 2))
                    if (px.r, px.g, px.b) == (255, 0, 255):
                        continue
                except Exception:
                    pass
                sub = pygame.transform.scale(sub, (int(frame_w * scale), int(sheet_h * scale)))
                frames.append(sub)
    except Exception:
        pass
    return frames

riklys_a_frames = build_sheet_frames(RIKLYS_SHEET_A_PATH, RIKLYS_SHEET_FRAMES, RIKLYS_SCALE)
riklys_b_frames = build_sheet_frames(RIKLYS_SHEET_B_PATH, RIKLYS_SHEET_FRAMES, RIKLYS_SCALE)
# fallback placeholders if loading failed
if not riklys_a_frames:
    placeholder = pygame.Surface((32 * RIKLYS_SCALE, 16 * RIKLYS_SCALE), pygame.SRCALPHA)
    pygame.draw.rect(placeholder, (200, 200, 200), placeholder.get_rect(), 2)
    riklys_a_frames = [placeholder]
if not riklys_b_frames:
    riklys_b_frames = riklys_a_frames.copy()

# sharks list (world coords)
underwater_sharks = []   # each: {"x","y","dx","state","frame_idx","frame_tick","rect"}
# shark behaviour params
SHARK_PATROL_SPEED = 1.0
SHARK_ATTACK_SPEED = 2.4
SHARK_ATTACK_RANGE = 140     # start attack when player closer than this (pixels)
SHARK_PATROL_TURN_CHANCE = 0.01

def spawn_sharks(n=2, x_min=200, x_max=None):
    """Spawn n sharks in the given world x range."""
    if x_max is None:
        x_max = max(1000, WIDTH * 2)
    for _ in range(n):
        sx = random.randint(x_min, x_max)
        sy = random.randint(HEIGHT // 2 + 10, HEIGHT - 120)
        sdx = random.choice([-1, 1]) * SHARK_PATROL_SPEED
        if riklys_a_frames:
            w = riklys_a_frames[0].get_width()
            h = riklys_a_frames[0].get_height()
        else:
            w, h = 32, 16
        rect = pygame.Rect(sx, sy, w, h)
        underwater_sharks.append({
            "x": sx, "y": sy, "dx": sdx,
            "state": "patrol", "frame_idx": 0, "frame_tick": 0, "rect": rect
        })

# initialize player lives and load HP images (files: 1hp.png .. 5hp.png) before main loop
player_lives = 5

HP_DIR = os.path.join(IMAGES_DIR, "hp")
# tweak this to make HP icons larger/smaller
HP_SCALE = 3.0
hp_images = []
for i in range(1, 6):
    hp_path = os.path.join(HP_DIR, f"{i}hp.png")
    try:
        img = pygame.image.load(hp_path).convert_alpha()
        w, h = img.get_size()
        img = pygame.transform.scale(img, (int(w * HP_SCALE), int(h * HP_SCALE)))
        hp_images.append(img)
    except Exception:
        # fallback placeholder sized according to HP_SCALE
        placeholder = pygame.Surface((64 * int(HP_SCALE), 16 * int(HP_SCALE)), pygame.SRCALPHA)
        pygame.draw.rect(placeholder, (255, 0, 0), placeholder.get_rect(), 2)
        hp_images.append(placeholder)

# add invulnerability timing so player can't be hit repeatedly in the same frame/short window
INVULN_MS = 1500               # milliseconds of invulnerability after a hit
player_invuln_until = 0

# dead icon for caught-fish indicator
dead_path = os.path.join(IMAGES_DIR, "dead.png")
dead_img = safe_load(dead_path, convert_alpha=True)
# optional scale (adjust DEAD_ICON_SCALE as needed)
DEAD_ICON_SCALE = 1.5
try:
    dead_img = pygame.transform.scale(dead_img, (int(dead_img.get_width() * DEAD_ICON_SCALE), int(dead_img.get_height() * DEAD_ICON_SCALE)))
except Exception:
    pass

# --- Underwater platforms ---
platform_img_path = os.path.join(IMAGES_DIR, "platforma.png")
platform_img = safe_load(platform_img_path, convert_alpha=True)  # 178x109
underwater_platforms = []  # list of pygame.Rect
PLATFORM_TOP_COLLIDE_H = 20  # tik viršutinė 20px juosta "kieta" atsistoti

# --- Bubbles (burbulai) sprite sheet: 80x8 (10 frames horizontally, 8x8 each) ---
burbulai_frames = []
try:
    burb_sheet = pygame.image.load(os.path.join(IMAGES_DIR, "burbulai.png")).convert_alpha()
    frame_w, frame_h, frames_count = 8, 8, 10
    BUBBLE_SCALE = 3
    for i in range(frames_count):
        sub = burb_sheet.subsurface((i * frame_w, 0, frame_w, frame_h)).copy()
        sub = pygame.transform.scale(sub, (frame_w * BUBBLE_SCALE, frame_h * BUBBLE_SCALE))
        burbulai_frames.append(sub)
except Exception:
    # fallback single frame
    ph = pygame.Surface((8 * 3, 8 * 3), pygame.SRCALPHA)
    pygame.draw.circle(ph, (180, 220, 255), (12, 12), 10, 2)
    burbulai_frames = [ph]

# bubbles state + params
bubbles = []  # {"x","y","vx","vy","born_ms","frame_idx","frame_tick","rect"}
BUBBLE_SPEED = 6.0
BUBBLE_LIFETIME_MS = 1500
BUBBLE_COOLDOWN_MS = 120
last_bubble_ms = 0

# underwater facing for blizgė flip
uw_facing_left = False

# shark slow effect from bubbles
SHARK_SLOW_MS = 2000

# --- Main game loop ---
while running:
   # capture events once; record E presses into a flag
   e_pressed = False
   for event in pygame.event.get():
       if event.type == pygame.QUIT:
           running = False
       elif event.type == pygame.KEYDOWN:
           if event.key == pygame.K_e:
               e_pressed = True

   # --- Movement ---
   keys = pygame.key.get_pressed()
   moving = False


   # Only scroll if background is wider than window
   can_scroll = bg_width > WIDTH


   if keys[pygame.K_a]:
       facing_left = True
       moving = True
       if cat_x > LEFT_MARGIN or not can_scroll or scroll_x == 0:
           cat_x -= speed
       elif can_scroll and scroll_x < 0:
           scroll_x += speed
   elif keys[pygame.K_d]:
       facing_left = False
       moving = True
       if cat_x < RIGHT_MARGIN or not can_scroll or scroll_x == -(bg_width - WIDTH):
           cat_x += speed
       elif can_scroll and scroll_x > -(bg_width - WIDTH):
           scroll_x -= speed


   # --- Clamp values ---
   cat_x = max(0, min(cat_x, WIDTH - FRAME_WIDTH * SCALE))
   if can_scroll:
       scroll_x = max(min(scroll_x, 0), -(bg_width - WIDTH))
   else:
       scroll_x = 0

   # --- Move varna animals randomly ---
   for animal in varna_animals:
       animal["x"] += animal["dx"]
       animal["y"] += animal["dy"]
       # Bounce off screen edges (sky area: y < 300)
       if animal["x"] < 0 or animal["x"] > WIDTH - VARNA_FRAME_WIDTH * VARNA_SCALE:
           animal["dx"] *= -1
       if animal["y"] < 0 or animal["y"] > 300:
           animal["dy"] *= -1

   # --- Animation updates ---
   if moving:
       current_frame = (current_frame + 0.2) % NUM_FRAMES
   else:
       current_frame = 0

   varna_anim_frame = (varna_anim_frame + 0.1) % VARNA_NUM_FRAMES
   zuvys_anim_frame = (zuvys_anim_frame + 0.03) % ZUVYS_NUM_FRAMES

   # --- Interaction: detect proximity to fish ---
   # compute cat center
   cat_center_x = cat_x + (FRAME_WIDTH * SCALE) / 2
   cat_center_y = cat_y + (FRAME_HEIGHT * SCALE) / 2

   nearest_fish = None
   nearest_dist = 99999
   for pos in zuvys_positions:
       fish_center_x = pos[0] + (ZUVYS_FRAME_WIDTH * ZUVYS_SCALE) / 2
       fish_center_y = pos[1] + (ZUVYS_FRAME_HEIGHT * ZUVYS_SCALE) / 2
       dist = ((cat_center_x - fish_center_x)**2 + (cat_center_y - fish_center_y)**2)**0.5
       if dist < nearest_dist:
           nearest_dist = dist
           nearest_fish = pos

   PROXIMITY_THRESHOLD = 140  # pixels
   near_fish = (nearest_dist <= PROXIMITY_THRESHOLD)

   # Start casting if E was pressed this frame and we're near a fish
   if e_pressed and near_fish and not casting:
       casting = True
       uzmesti_anim_frame = 0.0

   frame = frames[int(current_frame)]
   if facing_left:
       frame = pygame.transform.flip(frame, True, False)

   # --- Draw ---
   screen.fill((0, 0, 0))
   screen.blit(background, (0, 0))  # Always fills window

   # If dugnas (underwater) scene is active, run underwater mini-game and skip normal world rendering
   if show_dugnas:
       # background
       screen.blit(dugnas, (0, 0))
       # draw platforms
       for plat in underwater_platforms:
           screen.blit(platform_img, plat.topleft)

       # --- Update + draw underwater fish (use frames if available) ---
       for fish in underwater_fish[:]:
           # movement
           fish["x"] += fish["dx"]
           # reverse at screen edges
           if fish["x"] <= 10 or fish["x"] >= WIDTH - fish["rect"].width - 10:
               fish["dx"] *= -1
           fish["rect"].x = int(fish["x"])
           fish["rect"].y = int(fish["y"])
           # collide with platforms -> bounce horizontally only at sides (avoid sticking on top)
           for plat in underwater_platforms:
               if fish["rect"].colliderect(plat):
                   # only respond if overlapping platform's sides (ignore top area)
                   if fish["rect"].centery > plat.top + PLATFORM_TOP_COLLIDE_H:
                       if fish["rect"].centerx < plat.centerx and fish["rect"].right > plat.left:
                           fish["x"] = plat.left - fish["rect"].width
                       elif fish["rect"].centerx >= plat.centerx and fish["rect"].left < plat.right:
                           fish["x"] = plat.right
                       fish["dx"] *= -1
                       fish["rect"].x = int(fish["x"])
                       break

           # animate fish if frames exist
           if zuvis_a_frames:
               # simple per-fish frame tick
               fish["frame_tick"] = fish.get("frame_tick", 0) + 1
               if fish["frame_tick"] >= 8:
                   fish["frame_tick"] = 0
                   fish["frame_idx"] = (fish.get("frame_idx", 0) + 1) % len(zuvis_a_frames)
               img = zuvis_a_frames[fish.get("frame_idx", 0)]
           else:
               img = zuvis_a_img

           # flip sprite when moving left
           if fish["dx"] < 0:
               img = pygame.transform.flip(img, True, False)

           screen.blit(img, (int(fish["x"]), int(fish["y"])))

       # --- Underwater player physics & movement ---
       # Horizontal move across full screen; gravity constantly pulls player down
       keys = pygame.key.get_pressed()
       prev_x, prev_y = uw_player_x, uw_player_y
       # ankstesnis stačiakampis prieš fizikos atnaujinimą (naudojamas tikrinimui)
       prev_rect = pygame.Rect(int(prev_x - blizge_img.get_width() // 2), int(prev_y), blizge_img.get_width(), blizge_img.get_height())
       if keys[pygame.K_a] or keys[pygame.K_LEFT]:
           uw_player_x -= UW_SPEED
       if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
           uw_player_x += UW_SPEED
       # optional swim up (brief negative impulse)
       if keys[pygame.K_w] or keys[pygame.K_UP]:
           uw_player_vy = -5.5

       # apply gravity
       uw_player_vy += GRAVITY
       uw_player_y += uw_player_vy

       # clamp to screen edges and bottom
       player_w = blizge_img.get_width()
       player_h = blizge_img.get_height()
       uw_player_x = max(0 + player_w // 2, min(uw_player_x, WIDTH - player_w // 2))
       bottom_y = HEIGHT - player_h - 10
       if uw_player_y >= bottom_y:
           uw_player_y = bottom_y
           uw_player_vy = 0.0

       # resolve collisions with platforms (tik viršus kietas; šonai tik blokuoja)
       p_rect = pygame.Rect(int(uw_player_x - player_w // 2), int(uw_player_y), player_w, player_h)
       prev_rect = pygame.Rect(int(prev_x - player_w // 2), int(prev_y), player_w, player_h)
       for plat in underwater_platforms:
           # kieta tik viršutinė platformos juosta
           plat_top = pygame.Rect(plat.x, plat.y, plat.width, max(28, PLATFORM_TOP_COLLIDE_H))
           # leidžiame kristi laisvai, išskyrus kai šį frame kirtome viršų
           crossing_top = (
               uw_player_vy > 0 and
               prev_rect.bottom <= plat_top.top and
               p_rect.bottom >= plat_top.top and
               p_rect.centerx >= plat.left and p_rect.centerx <= plat.right
           )
           if crossing_top:
               # pastatyk ant viršaus
               uw_player_y = plat_top.top - player_h
               uw_player_vy = 0.0
               p_rect.y = int(uw_player_y)
               # pereik prie kitos platformos (nebeblokuok šonais šiame frame)
               continue
           # šonai: blokuoti tik jei aiškiai ne ant viršaus
           if p_rect.colliderect(plat) and p_rect.bottom > plat_top.top + 2:
               # nustatyk atėjimo pusę pagal ankstesnę padėtį
               if prev_rect.right <= plat.left and p_rect.right > plat.left:
                   uw_player_x = plat.left - player_w // 2
               elif prev_rect.left >= plat.right and p_rect.left < plat.right:
                   uw_player_x = plat.right + player_w // 2
               p_rect.x = int(uw_player_x - player_w // 2)

       # update underwater facing based on last horizontal input
       if keys[pygame.K_a] or keys[pygame.K_LEFT]:
           uw_facing_left = True
       elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
           uw_facing_left = False

       # spawn bubbles with F (cooldown)
       now_ms = pygame.time.get_ticks()
       if keys[pygame.K_f] and (now_ms - last_bubble_ms) >= BUBBLE_COOLDOWN_MS and burbulai_frames:
           spawn_x = uw_player_x + (-player_w // 2 if uw_facing_left else player_w // 2)
           spawn_y = uw_player_y + int(player_h * 0.4)
           vx = -BUBBLE_SPEED if uw_facing_left else BUBBLE_SPEED
           vy = -0.5  # slight rise
           bw = burbulai_frames[0].get_width()
           bh = burbulai_frames[0].get_height()
           rect = pygame.Rect(int(spawn_x), int(spawn_y), bw, bh)
           bubbles.append({
               "x": float(spawn_x), "y": float(spawn_y),
               "vx": vx, "vy": vy,
               "born_ms": now_ms,
               "frame_idx": 0, "frame_tick": 0,
               "rect": rect
           })
           last_bubble_ms = now_ms

       # draw player centered on (uw_player_x, uw_player_y)
       blizge_draw = blizge_img
       if uw_facing_left:
           blizge_draw = pygame.transform.flip(blizge_img, True, False)
       screen.blit(blizge_draw, (int(uw_player_x - player_w // 2), int(uw_player_y)))

       # draw hook (optional marker) at cast position
       # kabliukas nebus rodomas kaip geltonas kvadratas (pašalinta)

       # instructions + caught counter (Lithuanian)
       small = pygame.font.SysFont('Arial', 24)
       info = small.render("Valdymas: W/↑ - plaukti aukštyn | A/D - kairė/dešinė | SPACE - gaudyti | ENTER - grįžti", True, (255,255,255))
       screen.blit(info, (20, 20))
       # show dead icon + numeric caught count
       icon_x, icon_y = 20, 50
       if 'dead_img' in globals() and dead_img:
           screen.blit(dead_img, (icon_x, icon_y))
           cnt_surf = small.render(str(caught_count), True, (255, 255, 255))
           screen.blit(cnt_surf, (icon_x + dead_img.get_width() + 8, icon_y + (dead_img.get_height() - cnt_surf.get_height()) // 2))
       else:
           score = small.render(f"Pagauta žuvų: {caught_count}", True, (255,255,255))
           screen.blit(score, (20, 50))

       # coins collected indicator
       coins_surf = small.render(f"Monetos: {coins_collected} (kas 3 = +1 gyvybė)", True, (255, 230, 120))
       screen.blit(coins_surf, (20, 80))

       # attempt catch on SPACE: check collision between player rect and fish rect
       if keys[pygame.K_SPACE]:
           p_rect = pygame.Rect(int(uw_player_x - player_w // 2), int(uw_player_y), player_w, player_h)
           for fish in underwater_fish[:]:
               if fish["rect"].colliderect(p_rect):
                   underwater_fish.remove(fish)
                   caught_count += 1
                   # play reelin sound when a fish is caught
                   try:
                       if 'reelin_sound' in globals() and reelin_sound:
                           reelin_sound.play()
                   except Exception:
                       pass

       # return to surface
       if keys[pygame.K_RETURN]:
           if underwater_fish:
               # feedback: cannot return while fish remain
               warn = small.render("Negalite grįžti — sugaukite visas žuvis", True, (255, 80, 80))
               warn_rect = warn.get_rect(center=(WIDTH // 2, HEIGHT - 80))
               screen.blit(warn, warn_rect)
           else:
               # If all underwater fish were caught for this spot, disable that surface fishing spot
               if current_fishing_spot is not None:
                   try:
                       zuvys_positions.remove(current_fishing_spot)
                   except ValueError:
                       pass
                   disabled_spots.add(current_fishing_spot)
               # clear underwater state and return
               show_dugnas = False
               underwater_fish.clear()
               cast_hook_x = None
               cast_hook_y = None
               current_fishing_spot = None
               last_spawned_count = 0

       # --- Update + draw bubbles (burbulai) ---
       for b in bubbles[:]:
           # animate
           b["frame_tick"] += 1
           if b["frame_tick"] >= 4:
               b["frame_tick"] = 0
               b["frame_idx"] = (b["frame_idx"] + 1) % len(burbulai_frames)
           # move
           b["x"] += b["vx"]
           b["y"] += b["vy"]
           b["rect"].x = int(b["x"])
           b["rect"].y = int(b["y"])
           # lifetime
           if pygame.time.get_ticks() - b["born_ms"] >= BUBBLE_LIFETIME_MS:
               bubbles.remove(b)
               continue
           # collide with platforms -> pop bubble
           popped = False
           for plat in underwater_platforms:
               if b["rect"].colliderect(plat):
                   bubbles.remove(b)
                   popped = True
                   break
           if popped:
               continue
           # collide with sharks -> apply slow and pop bubble
           for shark in underwater_sharks:
               if shark["rect"].colliderect(b["rect"]):
                   shark["slow_until"] = pygame.time.get_ticks() + SHARK_SLOW_MS
                   if b in bubbles:
                       bubbles.remove(b)
                   break
           # draw bubble
           img_b = burbulai_frames[b["frame_idx"]]
           screen.blit(img_b, (int(b["x"] - uw_scroll_x), int(b["y"])))

       # --- Update + draw coins ---
       for c in coins[:]:
          # animate
          c["frame_tick"] += 1
          if c["frame_tick"] >= 6:
              c["frame_tick"] = 0
              c["frame_idx"] = (c["frame_idx"] + 1) % len(coin_frames)
          # player collision
          p_rect = pygame.Rect(int(uw_player_x - blizge_img.get_width() // 2), int(uw_player_y), blizge_img.get_width(), blizge_img.get_height())
          if p_rect.colliderect(c["rect"]):
              coins.remove(c)
              # sound
              try:
                  if coin_sound:
                      coin_sound.play()
              except Exception:
                  pass
              # count + life every 3
              coins_collected += 1
              if coins_collected % 3 == 0:
                  player_lives = min(player_lives + 1, 9)
              continue
          # draw coin (world->screen, consistent with bubbles/sharks if using uw_scroll_x)
          coin_img = coin_frames[c["frame_idx"]]
          screen.blit(coin_img, (int(c["x"] - uw_scroll_x), int(c["y"])))

       # --- Update + draw sharks (riklys) ---
       now_ms = pygame.time.get_ticks()
       for shark in underwater_sharks[:]:
           slow_active = now_ms < shark.get("slow_until", 0)
           speed_factor = 0.5 if slow_active else 1.0

           # distance to player (player world coords: uw_player_x, uw_player_y)
           dxp = (uw_player_x - shark["x"])
           dyp = (uw_player_y - shark["y"])
           dist = (dxp * dxp + dyp * dyp) ** 0.5

           # decide state
           if dist <= SHARK_ATTACK_RANGE:
               shark["state"] = "attack"
               # move toward player
               norm = dist if dist != 0 else 1
               shark["dx"] = (dxp / norm) * (SHARK_ATTACK_SPEED * speed_factor)
               shark["y"] += (dyp / norm) * (0.6 * speed_factor)
           else:
               # patrol behaviour
               if shark["state"] != "patrol":
                   shark["state"] = "patrol"
                   shark["dx"] = random.choice([-1, 1]) * (SHARK_PATROL_SPEED * speed_factor)
               # random turn
               if random.random() < SHARK_PATROL_TURN_CHANCE:
                   shark["dx"] = -shark["dx"]
               # gentle vertical bobbing
               shark["y"] += math.sin(pygame.time.get_ticks() / 600.0 + shark["x"]) * 0.2

           # ensure patrol speed magnitude reflects slow
           if shark["state"] == "patrol":
               shark["dx"] = math.copysign(SHARK_PATROL_SPEED * speed_factor, shark["dx"])

           # apply horizontal move & clamp to world
           shark["x"] += shark["dx"]
           if shark["x"] < 10:
               shark["x"] = 10
               shark["dx"] *= -1
           if shark["x"] > WIDTH - shark["rect"].width - 10:
               shark["x"] = WIDTH - shark["rect"].width - 10
               shark["dx"] *= -1

           shark["rect"].x = int(shark["x"])
           shark["rect"].y = int(shark["y"])

           # animate appropriate frame set
           shark["frame_tick"] = shark.get("frame_tick", 0) + 1
           if shark["frame_tick"] >= 8:
               shark["frame_tick"] = 0
               shark["frame_idx"] = (shark.get("frame_idx", 0) + 1) % RIKLYS_SHEET_FRAMES

           if shark["state"] == "attack":
               img = riklys_b_frames[shark["frame_idx"] % len(riklys_b_frames)]
           else:
               img = riklys_a_frames[shark["frame_idx"] % len(riklys_a_frames)]

           # flip when moving left
           if shark["dx"] < 0:
               img = pygame.transform.flip(img, True, False)

           # draw shark (world->screen)
           screen.blit(img, (int(shark["x"] - uw_scroll_x), int(shark["y"])))

           # collision with player — apply invulnerability window after a hit
           if now_ms >= player_invuln_until:
               p_rect = pygame.Rect(int(uw_player_x - blizge_img.get_width() // 2), int(uw_player_y), blizge_img.get_width(), blizge_img.get_height())
               p_hit = p_rect.inflate(-int(p_rect.width * 0.4), -int(p_rect.height * 0.4))   # shrink player hitbox
               s_hit = shark["rect"].inflate(-int(shark["rect"].width * 0.6), -int(shark["rect"].height * 0.6))  # shrink shark hitbox
               if s_hit.colliderect(p_hit):
                   # apply damage and activate invulnerability
                   player_lives -= 1
                   try:
                       if hurt_sound:
                           hurt_sound.play()
                   except Exception:
                       pass
                   player_invuln_until = now_ms + INVULN_MS
                   # knockback
                   if shark["x"] < uw_player_x:
                       uw_player_x += 40
                   else:
                       uw_player_x -= 40
                   # if lives depleted, clear underwater and return to surface
                   if player_lives <= 0:
                       show_dugnas = False
                       underwater_fish.clear()
                       underwater_sharks.clear()
                       cast_hook_x = None
                       cast_hook_y = None
                       current_fishing_spot = None
                       last_spawned_count = 0
                       break

       # draw player lives
       # draw player lives using hp images (1hp..5hp). index = player_lives - 1 (clamped)
       if 'hp_images' in globals() and hp_images:
           hp_idx = max(0, min(player_lives - 1, len(hp_images) - 1))
           hp_img = hp_images[hp_idx]
           screen.blit(hp_img, (WIDTH - hp_img.get_width() - 20, 20))
       else:
           small = pygame.font.SysFont('Arial', 24)
           lives_surf = small.render(f"Gyvybės: {player_lives}", True, (255, 200, 50))
           screen.blit(lives_surf, (WIDTH - 180, 20))

       pygame.display.flip()
       clock.tick(60)
       continue

   # Draw game title
   screen.blit(title_surface, title_rect)

   # Draw varna animals
   for animal in varna_animals:
       varna_frame = varna_frames[int(varna_anim_frame)]
       screen.blit(varna_frame, (int(animal["x"]), int(animal["y"])))


   # Draw zuvys animals
   for pos in zuvys_positions:
       zuvys_frame = zuvys_frames[int(zuvys_anim_frame)]
       screen.blit(zuvys_frame, pos)


   # Draw player (hidden while casting so the cast animation replaces the player)
   if not casting:
      screen.blit(frame, (cat_x, cat_y))


   # Draw Press-E prompt when near fish (and not casting)
   if near_fish and not casting and press_e_frames:
       press_frame = press_e_frames[int(press_e_anim_frame) % len(press_e_frames)]
       # place prompt above the nearest fish
       prompt_x = nearest_fish[0] + (ZUVYS_FRAME_WIDTH * ZUVYS_SCALE) // 2 - press_frame.get_width() // 2
       prompt_y = nearest_fish[1] - press_frame.get_height() - 10
       screen.blit(press_frame, (int(prompt_x), int(prompt_y)))
       press_e_anim_frame = (press_e_anim_frame + 0.15) % len(press_e_frames)

   # Play uzmeti (cast) animation when casting
   if casting and uzmesti_frames:
       idx = int(uzmesti_anim_frame)
       if idx >= len(uzmesti_frames):
           # finished -> show dugnas scene and spawn fish; record last hook spot
           casting = False
           uzmesti_anim_frame = 0.0
           # compute hand position (same logic as used for drawing)
           HAND_REL_X_RIGHT = 0.75
           HAND_REL_X_LEFT = 0.25
           HAND_REL_Y = 0.55
           hand_x = cat_x + int((HAND_REL_X_LEFT if facing_left else HAND_REL_X_RIGHT) * FRAME_WIDTH * SCALE)
           hand_y = cat_y + int(HAND_REL_Y * FRAME_HEIGHT * SCALE)
           cast_hook_x = hand_x
           cast_hook_y = hand_y
           # spawn underwater fish for the mini-game and remember which surface spot we came from
           current_fishing_spot = nearest_fish
           spawn_underwater_fish(6)

           # spawn sharks so they are visible during the mini-game
           # place sharks near the hook (adjust counts / ranges as needed)
           underwater_sharks.clear()
           try:
               sx_min = int(cast_hook_x + 60)
               sx_max = int(cast_hook_x + 400)
           except Exception:
               sx_min = 200
               sx_max = 800
           spawn_sharks(n=2, x_min=sx_min, x_max=sx_max)

           # initialize underwater player position near the hook/top
           uw_player_x = cast_hook_x if cast_hook_x is not None else WIDTH // 2
           uw_player_y = max(30, int(cast_hook_y + 10))  # start a bit below hook
           uw_player_vy = 0.0

           # spawn a few static platforms underwater (simple layout)
           underwater_platforms.clear()
           pw, ph = platform_img.get_width(), platform_img.get_height()
           for px, py in [(300, HEIGHT//2 + 40), (860, HEIGHT//2 + 70)]:
               underwater_platforms.append(pygame.Rect(px, py, pw, ph))

           # spawn 1–2 coins near platforms
           coins.clear()
           if coin_frames:
               cw, ch = coin_frames[0].get_width(), coin_frames[0].get_height()
               for cx, cy in [(300 + pw // 2, HEIGHT//2 + 10), (860 + pw // 2, HEIGHT//2 + 20)]:
                   rect = pygame.Rect(cx, cy, cw, ch)
                   coins.append({"x": cx, "y": cy, "rect": rect, "frame_idx": 0, "frame_tick": 0})

           show_dugnas = True
       else:
          uz_frame = uzmesti_frames[idx]

          # flip before measuring
          if facing_left:
              uz_frame = pygame.transform.flip(uz_frame, True, False)

          # Anchor to a relative "hand" point on the cat sprite (tweak these)
          HAND_REL_X_RIGHT = 0.5  # fraction across cat sprite where hand is when facing right
          HAND_REL_X_LEFT = 0.5   # fraction across cat sprite where hand is when facing left
          HAND_REL_Y = 0.5        # fraction down from cat top to hand

          if facing_left:
              hand_x = cat_x + int(HAND_REL_X_LEFT * FRAME_WIDTH * SCALE)
          else:
              hand_x = cat_x + int(HAND_REL_X_RIGHT * FRAME_WIDTH * SCALE)
          hand_y = cat_y + int(HAND_REL_Y * FRAME_HEIGHT * SCALE)

          cast_x = hand_x - uz_frame.get_width() // 2
          cast_y = hand_y - uz_frame.get_height() // 2

          screen.blit(uz_frame, (int(cast_x), int(cast_y)))
          uzmesti_anim_frame += 0.4

   pygame.display.flip()
   clock.tick(60)

pygame.quit()





