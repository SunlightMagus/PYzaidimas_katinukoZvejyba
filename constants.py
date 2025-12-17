"""
Žaidimo konstantos ir konfigūracija
"""

# --- Lango nustatymai ---
WIDTH, HEIGHT = 1280, 720

# --- Pasaulio nustatymai ---
WORLD_WIDTH = 6000

# --- Animacijų nustatymai ---
FRAME_WIDTH = 128
FRAME_HEIGHT = 128
NUM_FRAMES = 5
SCALE = 2

# --- Žaidėjo nustatymai ---
SPEED = 8
LEFT_MARGIN = WIDTH // 3
RIGHT_MARGIN = WIDTH - WIDTH // 3 - FRAME_WIDTH * SCALE

# --- Varnų nustatymai ---
VARNA_FRAME_WIDTH = 64
VARNA_FRAME_HEIGHT = 64
VARNA_NUM_FRAMES = 5
VARNA_SCALE = 2

# --- Žuvų nustatymai ---
ZUVYS_FRAME_WIDTH = 64
ZUVYS_FRAME_HEIGHT = 64
ZUVYS_NUM_FRAMES = 4
ZUVYS_SCALE = 2
ZUVA_SCALE = 3
BLIZGE_SCALE = 0.5

# --- Press-E / Uzmesti animacijos ---
PRESS_E_FRAME_WIDTH = 64
PRESS_E_FRAME_HEIGHT = 64
PRESS_E_NUM_FRAMES = 4
PRESS_E_SCALE = 2

UZM_FRAME_WIDTH = 128
UZM_FRAME_HEIGHT = 128
UZM_NUM_FRAMES = 6
UZM_SCALE = 2

# --- Ryklių nustatymai ---
RIKLYS_SHEET_FRAMES = 8
RIKLYS_SCALE = 3
SHARK_PATROL_SPEED = 1.0
SHARK_ATTACK_SPEED = 2.4
SHARK_ATTACK_RANGE = 140
SHARK_PATROL_TURN_CHANCE = 0.01
SHARK_SLOW_MS = 2000

# --- Žaidėjo gyvybės ---
MAX_LIVES = 5
COST_PER_LIFE = 3
INVULN_MS = 1500

# --- HP ikonų nustatymai ---
HP_SCALE = 3.0

# --- Monetos nustatymai ---
COIN_SCALE = 2
ICON_SCALE = 1.5

# --- Dead ikona ---
DEAD_ICON_SCALE = 2.2

# --- Povandeninio žaidimo fizika ---
UW_SPEED = 3.0
GRAVITY = 0.35
PLATFORM_TOP_COLLIDE_H = 20

# --- Burbulai ---
BUBBLE_SCALE = 3
BUBBLE_SPEED = 6.0
BUBBLE_LIFETIME_MS = 1500
BUBBLE_COOLDOWN_MS = 120

# --- Žvejybos nustatymai ---
PROXIMITY_THRESHOLD = 140

# --- Lygių sistema ---
SPOTS_PER_LEVEL = 3  # Kiek telkinių reikia sugaudyti, kad pereiti į kitą lygį
