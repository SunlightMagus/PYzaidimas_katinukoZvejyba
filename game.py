import pygame
import os
import random


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


background_path = os.path.join(IMAGES_DIR, "ezeras.png")
sprite_sheet_path = os.path.join(IMAGES_DIR, "valtis_anim.png")
varna_sheet_path = os.path.join(IMAGES_DIR, "varna_Sheet.png")
zuvys_sheet_path = os.path.join(IMAGES_DIR, "zuvys_sheet.png")

# new sheets for prompt/cast
press_e_path = os.path.join(IMAGES_DIR, "press_e_Sheet.png")
uzmesti_path = os.path.join(IMAGES_DIR, "uzmesti_Sheet.png")


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


# try load sheets; use placeholders on failure (we'll check bounds when slicing)
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

   # Play uzmesti (cast) animation when casting
   if casting and uzmesti_frames:
       idx = int(uzmesti_anim_frame)
       if idx >= len(uzmeti_frames := uzmesti_frames):  # safe local alias for clarity
           # finished
           casting = False
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





