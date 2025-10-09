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


background = pygame.image.load(background_path).convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))  # Scale to fit window
bg_width = WIDTH
bg_height = HEIGHT


sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()


# --- Animation setup ---
FRAME_WIDTH = 128
FRAME_HEIGHT = 128
NUM_FRAMES = 5
SCALE = 2


frames = []
for i in range(NUM_FRAMES):
   frame = sprite_sheet.subsurface((i * FRAME_WIDTH, 0, FRAME_WIDTH, FRAME_HEIGHT))
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


varna_sheet = pygame.image.load(varna_sheet_path).convert_alpha()
varna_frames = []
for i in range(VARNA_NUM_FRAMES):
   frame = varna_sheet.subsurface((i * VARNA_FRAME_WIDTH, 0, VARNA_FRAME_WIDTH, VARNA_FRAME_HEIGHT))
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


zuvys_sheet = pygame.image.load(zuvys_sheet_path).convert_alpha()
zuvys_frames = []
for i in range(ZUVYS_NUM_FRAMES):
   frame = zuvys_sheet.subsurface((i * ZUVYS_FRAME_WIDTH, 0, ZUVYS_FRAME_WIDTH, ZUVYS_FRAME_HEIGHT))
   frame = pygame.transform.scale(frame, (ZUVYS_FRAME_WIDTH * ZUVYS_SCALE, ZUVYS_FRAME_HEIGHT * ZUVYS_SCALE))
   zuvys_frames.append(frame)


# Positions for fish near the middle of the scene
zuvys_positions = [
   (WIDTH // 2 - 100, HEIGHT // 2 + 150),
]


zuvys_anim_frame = 0


while running:
   for event in pygame.event.get():
       if event.type == pygame.QUIT:
           running = False


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


   # --- Animation ---
   if moving:
       current_frame = (current_frame + 0.2) % NUM_FRAMES
   else:
       current_frame = 0


   # Loop varna animation
   varna_anim_frame = (varna_anim_frame + 0.1) % VARNA_NUM_FRAMES


   # Loop zuvys animation
   zuvys_anim_frame = (zuvys_anim_frame + 0.03) % ZUVYS_NUM_FRAMES


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


   screen.blit(frame, (cat_x, cat_y))


   pygame.display.flip()
   clock.tick(60)


pygame.quit()





