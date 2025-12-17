"""
Žaidimo išteklių (paveikslėlių, garsų) užkrovimas
"""
import pygame
import os
from constants import *


# --- Kelio nustatymai ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images")
SOUNDS_DIR = os.path.join(BASE_DIR, "sounds")


def safe_load(path, convert_alpha=False, size=None, fill_color=(255, 0, 255, 128)):
    """Saugiai užkrauna paveikslėlį, arba sukuria placeholder"""
    try:
        img = pygame.image.load(path)
        img = img.convert_alpha() if convert_alpha else img.convert()
        if size is not None:
            img = pygame.transform.scale(img, size)
        return img
    except Exception:
        w, h = size if size else (128, 128)
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        pygame.draw.rect(surf, (255, 0, 255), surf.get_rect(), 3)
        return surf


def load_sprite_sheet(sheet_path, frame_width, frame_height, num_frames, scale):
    """Užkrauna sprite sheet ir grąžina kadrų sąrašą"""
    frames = []
    try:
        sprite_sheet = pygame.image.load(sheet_path).convert_alpha()
    except Exception:
        sprite_sheet = None

    for i in range(num_frames):
        if sprite_sheet:
            sheet_w = sprite_sheet.get_width()
            if (i + 1) * frame_width <= sheet_w:
                frame = sprite_sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
            else:
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                pygame.draw.rect(frame, (255, 0, 255), frame.get_rect(), 2)
        else:
            frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            pygame.draw.rect(frame, (255, 0, 255), frame.get_rect(), 2)
        
        frame = pygame.transform.scale(frame, (frame_width * scale, frame_height * scale))
        frames.append(frame)
    
    return frames


def build_sheet_frames(path, frames_count=8, scale=3):
    """Sukuria kadrus iš sprite sheet (naudojama rykliams)"""
    frames = []
    try:
        sheet = pygame.image.load(path).convert_alpha()
        sheet_w, sheet_h = sheet.get_width(), sheet.get_height()
        frame_w = max(1, sheet_w // frames_count)
        for i in range(frames_count):
            x = i * frame_w
            if x + frame_w <= sheet_w:
                sub = sheet.subsurface((x, 0, frame_w, sheet_h)).copy()
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


def load_assets():
    """Užkrauna visus žaidimo išteklius"""
    assets = {}
    
    # --- Pagrindiniai paveikslėliai ---
    bg_path = os.path.join(IMAGES_DIR, "ezeras.png")
    assets['background'] = safe_load(bg_path, convert_alpha=False, size=(WIDTH, HEIGHT))
    assets['bg_width'], assets['bg_height'] = assets['background'].get_size()
    
    # Antro lygio fonas
    bg2_path = os.path.join(IMAGES_DIR, "background2.png")
    assets['background2'] = safe_load(bg2_path, convert_alpha=False, size=(WIDTH, HEIGHT))
    assets['bg2_width'], assets['bg2_height'] = assets['background2'].get_size()
    
    assets['dugnas'] = safe_load(os.path.join(IMAGES_DIR, "dugnas.png"), 
                                  convert_alpha=False, size=(WIDTH, HEIGHT))
    assets['meniu_img'] = safe_load(os.path.join(IMAGES_DIR, "meniu.png"), 
                                     convert_alpha=True)
    
    # --- Animacijos ---
    assets['frames'] = load_sprite_sheet(
        os.path.join(IMAGES_DIR, "valtis_anim.png"),
        FRAME_WIDTH, FRAME_HEIGHT, NUM_FRAMES, SCALE
    )
    
    assets['varna_frames'] = load_sprite_sheet(
        os.path.join(IMAGES_DIR, "varna_Sheet.png"),
        VARNA_FRAME_WIDTH, VARNA_FRAME_HEIGHT, VARNA_NUM_FRAMES, VARNA_SCALE
    )
    
    assets['zuvys_frames'] = load_sprite_sheet(
        os.path.join(IMAGES_DIR, "zuvys_sheet.png"),
        ZUVYS_FRAME_WIDTH, ZUVYS_FRAME_HEIGHT, ZUVYS_NUM_FRAMES, ZUVYS_SCALE
    )
    
    assets['press_e_frames'] = load_sprite_sheet(
        os.path.join(IMAGES_DIR, "press_e_Sheet.png"),
        PRESS_E_FRAME_WIDTH, PRESS_E_FRAME_HEIGHT, PRESS_E_NUM_FRAMES, PRESS_E_SCALE
    )
    
    assets['uzmesti_frames'] = load_sprite_sheet(
        os.path.join(IMAGES_DIR, "uzmesti_Sheet.png"),
        UZM_FRAME_WIDTH, UZM_FRAME_HEIGHT, UZM_NUM_FRAMES, UZM_SCALE
    )
    
    # --- Povandenės žuvys ---
    zuvis_a_path = os.path.join(IMAGES_DIR, "Zuvis_A.png")
    zuvis_a_frames = []
    try:
        zuvis_a_sheet = pygame.image.load(zuvis_a_path).convert_alpha()
        SHEET_FRAMES = 8
        sheet_w = zuvis_a_sheet.get_width()
        sheet_h = zuvis_a_sheet.get_height()
        frame_w = max(1, sheet_w // SHEET_FRAMES)
        frame_h = sheet_h
        
        for i in range(SHEET_FRAMES):
            x = i * frame_w
            if x + frame_w <= sheet_w and frame_h <= sheet_h:
                sub = zuvis_a_sheet.subsurface((x, 0, frame_w, frame_h)).copy()
                try:
                    px = sub.get_at((frame_w // 2, frame_h // 2))
                    if (px.r, px.g, px.b) == (255, 0, 255):
                        continue
                except Exception:
                    pass
                sub = pygame.transform.scale(sub, (int(frame_w * ZUVA_SCALE), int(frame_h * ZUVA_SCALE)))
                zuvis_a_frames.append(sub)
    except Exception:
        pass
    
    if not zuvis_a_frames:
        zuvis_a_img = safe_load(zuvis_a_path, convert_alpha=True, 
                                size=(int(ZUVYS_FRAME_WIDTH * ZUVA_SCALE), 
                                      int(ZUVYS_FRAME_HEIGHT * ZUVA_SCALE)))
    else:
        zuvis_a_img = zuvis_a_frames[0]
    
    assets['zuvis_a_frames'] = zuvis_a_frames
    assets['zuvis_a_img'] = zuvis_a_img
    
    # --- Blizgė (povandeninis žaidėjas) ---
    assets['blizge_img'] = safe_load(
        os.path.join(IMAGES_DIR, "blizge.png"),
        convert_alpha=True,
        size=(int(ZUVYS_FRAME_WIDTH * ZUVA_SCALE * BLIZGE_SCALE),
              int(ZUVYS_FRAME_HEIGHT * ZUVA_SCALE * BLIZGE_SCALE))
    )
    
    # --- Rykliai ---
    assets['riklys_a_frames'] = build_sheet_frames(
        os.path.join(IMAGES_DIR, "riklys_a.png"),
        RIKLYS_SHEET_FRAMES, RIKLYS_SCALE
    )
    assets['riklys_b_frames'] = build_sheet_frames(
        os.path.join(IMAGES_DIR, "riklys_b.png"),
        RIKLYS_SHEET_FRAMES, RIKLYS_SCALE
    )
    
    # Fallback placeholders
    if not assets['riklys_a_frames']:
        placeholder = pygame.Surface((32 * RIKLYS_SCALE, 16 * RIKLYS_SCALE), pygame.SRCALPHA)
        pygame.draw.rect(placeholder, (200, 200, 200), placeholder.get_rect(), 2)
        assets['riklys_a_frames'] = [placeholder]
    if not assets['riklys_b_frames']:
        assets['riklys_b_frames'] = assets['riklys_a_frames'].copy()
    
    # --- HP ikonos ---
    hp_images = []
    HP_DIR = os.path.join(IMAGES_DIR, "hp")
    for i in range(1, 6):
        hp_path = os.path.join(HP_DIR, f"{i}hp.png")
        try:
            img = pygame.image.load(hp_path).convert_alpha()
            w, h = img.get_size()
            img = pygame.transform.scale(img, (int(w * HP_SCALE), int(h * HP_SCALE)))
            hp_images.append(img)
        except Exception:
            placeholder = pygame.Surface((64 * int(HP_SCALE), 16 * int(HP_SCALE)), pygame.SRCALPHA)
            pygame.draw.rect(placeholder, (255, 0, 0), placeholder.get_rect(), 2)
            hp_images.append(placeholder)
    assets['hp_images'] = hp_images
    
    # --- Dead ikona ---
    dead_img = safe_load(os.path.join(IMAGES_DIR, "dead.png"), convert_alpha=True)
    try:
        dead_img = pygame.transform.scale(dead_img, 
                                          (int(dead_img.get_width() * DEAD_ICON_SCALE),
                                           int(dead_img.get_height() * DEAD_ICON_SCALE)))
    except Exception:
        pass
    assets['dead_img'] = dead_img
    
    # --- Monetos ---
    coin_frames = []
    try:
        coin_sheet = pygame.image.load(os.path.join(IMAGES_DIR, "pinigas.png")).convert_alpha()
        frame_w, frame_h, frames_count = 16, 16, 8
        for i in range(frames_count):
            sub = coin_sheet.subsurface((i * frame_w, 0, frame_w, frame_h)).copy()
            sub = pygame.transform.scale(sub, (frame_w * COIN_SCALE, frame_h * COIN_SCALE))
            coin_frames.append(sub)
    except Exception:
        ph = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(ph, (255, 220, 0), (16, 16), 12)
        pygame.draw.circle(ph, (200, 160, 0), (16, 16), 12, 3)
        coin_frames = [ph]
    assets['coin_frames'] = coin_frames
    
    # Monetos ikona HUD
    try:
        pinigas_icon = pygame.image.load(os.path.join(IMAGES_DIR, "pinigas_ikona.png")).convert_alpha()
        iw, ih = pinigas_icon.get_size()
        pinigas_icon = pygame.transform.scale(pinigas_icon, (int(iw * ICON_SCALE), int(ih * ICON_SCALE)))
    except Exception:
        pinigas_icon = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(pinigas_icon, (255, 220, 0), (16, 16), 12)
    assets['pinigas_icon'] = pinigas_icon
    
    # --- Platforma ---
    assets['platform_img'] = safe_load(os.path.join(IMAGES_DIR, "platforma.png"), 
                                        convert_alpha=True)
    
    # --- Burbulai ---
    burbulai_frames = []
    try:
        burb_sheet = pygame.image.load(os.path.join(IMAGES_DIR, "burbulai.png")).convert_alpha()
        frame_w, frame_h, frames_count = 8, 8, 10
        for i in range(frames_count):
            sub = burb_sheet.subsurface((i * frame_w, 0, frame_w, frame_h)).copy()
            sub = pygame.transform.scale(sub, (frame_w * BUBBLE_SCALE, frame_h * BUBBLE_SCALE))
            burbulai_frames.append(sub)
    except Exception:
        ph = pygame.Surface((8 * 3, 8 * 3), pygame.SRCALPHA)
        pygame.draw.circle(ph, (180, 220, 255), (12, 12), 10, 2)
        burbulai_frames = [ph]
    assets['burbulai_frames'] = burbulai_frames
    
    return assets


def load_sounds():
    """Užkrauna visus žaidimo garsus"""
    sounds = {}
    
    # --- Foninė muzika ---
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
                pygame.mixer.music.play(-1)
            except Exception:
                pass
    except Exception:
        pass
    
    # --- Hurt sound ---
    hurt_sound = None
    try:
        hurt_path = os.path.join(SOUNDS_DIR, "hurt.mp3")
        if os.path.exists(hurt_path):
            try:
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
    sounds['hurt_sound'] = hurt_sound
    
    # --- Reelin sound ---
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
    sounds['reelin_sound'] = reelin_sound
    
    # --- Coin sound ---
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
    sounds['coin_sound'] = coin_sound
    
    return sounds
