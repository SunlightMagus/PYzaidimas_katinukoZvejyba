"""
Katinuko žvejyba - Pagrindinis žaidimo failas
"""
import pygame
import random
from constants import *
from assets import load_assets, load_sounds
from entities import Player, Varna, FishingSpot
from underwater import UnderwaterGame
from ui import UI


def draw_bg_tiled(screen, background, bg_width, scroll_x):
    """Nupiešia kartojamą foną"""
    start_x = -(abs(int(scroll_x)) % bg_width)
    x = start_x
    while x < WIDTH:
        screen.blit(background, (x, 0))
        x += bg_width


def get_current_background(assets, level):
    """Grąžina fono paveikslėlį pagal lygį"""
    if level == 2:
        return assets['background2'], assets['bg2_width']
    else:
        return assets['background'], assets['bg_width']


def ensure_surface_spot_ahead(fishing_spots, cat_world_x, min_dx=600, max_dx=1100):
    """Užtikrina, kad yra žvejybos vieta priekyje"""
    for spot in fishing_spots:
        if not spot.disabled and spot.x > cat_world_x:
            return
    
    nx = int(min(cat_world_x + random.randint(min_dx, max_dx), WORLD_WIDTH - 200))
    ny = HEIGHT // 2 + 150
    fishing_spots.append(FishingSpot(nx, ny))


def main():
    """Pagrindinis žaidimo ciklas"""
    pygame.init()
    pygame.font.init()
    
    # --- Lango nustatymai ---
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Katinuko žvejyba")
    clock = pygame.time.Clock()
    
    # --- Užkrauti išteklius ---
    assets = load_assets()
    sounds = load_sounds()
    
    # --- UI ---
    ui = UI(assets)
    
    # --- Žaidėjas ---
    player = Player(assets['frames'])
    
    # --- Varnos ---
    varnas = []
    for pos in [(300, 100), (700, 150), (1100, 80), (1600, 120)]:
        varnas.append(Varna(pos[0], pos[1]))
    varna_anim_frame = 0
    
    # --- Žvejybos taškai ---
    fishing_spots = [FishingSpot(WIDTH // 2 - 100, HEIGHT // 2 + 150)]
    zuvys_anim_frame = 0
    
    # --- Press-E animacija ---
    press_e_anim_frame = 0.0
    
    # --- Casting animacija ---
    casting = False
    uzmesti_anim_frame = 0.0
    
    # --- Povandeninis žaidimas ---
    underwater_game = UnderwaterGame(assets, sounds)
    show_dugnas = False
    current_fishing_spot = None
    
    # --- Žaidėjo būsena ---
    player_lives = 5
    player_invuln_until = 0
    coins_collected = 0
    caught_count = 0
    
    # --- Lygių sistema ---
    current_level = 1
    spots_completed = 0  # Kiek telkinių sugauta šiame lygyje
    level_transition_timer = 0  # Laikmatis lygio perėjimui
    show_level_message = False
    
    # --- Pasaulio scrolling ---
    scroll_x = 0
    
    # --- Meniu ---
    show_menu = False
    
    # --- Game Over ---
    game_over = False
    
    # --- Pagrindinis ciklas ---
    running = True
    while running:
        # --- Įvykių apdorojimas ---
        e_pressed = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    e_pressed = True
                elif event.key == pygame.K_ESCAPE:
                    show_menu = not show_menu
        
        # --- GAME OVER ---
        if game_over:
            screen.fill((0, 0, 0))
            
            # Game Over užrašas
            game_over_font = pygame.font.SysFont('Arial', 96, bold=True)
            go_text = game_over_font.render("ŽAIDIMAS BAIGTAS", True, (255, 50, 50))
            go_rect = go_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
            
            # Šešėlis
            shadow_text = game_over_font.render("ŽAIDIMAS BAIGTAS", True, (0, 0, 0))
            shadow_rect = shadow_text.get_rect(center=(WIDTH // 2 + 4, HEIGHT // 3 + 4))
            screen.blit(shadow_text, shadow_rect)
            screen.blit(go_text, go_rect)
            
            # Statistika
            stats_font = pygame.font.SysFont('Arial', 36)
            stats_text = f"Pagauta žuvų: {caught_count}  |  Surinkta monetų: {coins_collected}  |  Lygis: {current_level}"
            stats_surf = stats_font.render(stats_text, True, (255, 255, 255))
            stats_rect = stats_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
            screen.blit(stats_surf, stats_rect)
            
            # Mygtukai
            button_font = pygame.font.SysFont('Arial', 40, bold=True)
            
            # "Žaisti iš naujo" mygtukas
            restart_btn = pygame.Rect(WIDTH // 2 - 250, HEIGHT // 2 + 50, 220, 70)
            restart_color = (50, 200, 50)
            if restart_btn.collidepoint(pygame.mouse.get_pos()):
                restart_color = (80, 255, 80)
            pygame.draw.rect(screen, restart_color, restart_btn, border_radius=10)
            pygame.draw.rect(screen, (0, 0, 0), restart_btn, 3, border_radius=10)
            restart_text = button_font.render("Žaisti iš naujo", True, (0, 0, 0))
            restart_text_rect = restart_text.get_rect(center=restart_btn.center)
            screen.blit(restart_text, restart_text_rect)
            
            # "Išeiti" mygtukas
            quit_btn = pygame.Rect(WIDTH // 2 + 30, HEIGHT // 2 + 50, 220, 70)
            quit_color = (200, 50, 50)
            if quit_btn.collidepoint(pygame.mouse.get_pos()):
                quit_color = (255, 80, 80)
            pygame.draw.rect(screen, quit_color, quit_btn, border_radius=10)
            pygame.draw.rect(screen, (0, 0, 0), quit_btn, 3, border_radius=10)
            quit_text = button_font.render("Išeiti", True, (0, 0, 0))
            quit_text_rect = quit_text.get_rect(center=quit_btn.center)
            screen.blit(quit_text, quit_text_rect)
            
            # Mygtukų logika
            if pygame.mouse.get_pressed()[0]:
                mx, my = pygame.mouse.get_pos()
                if restart_btn.collidepoint(mx, my):
                    # Reset žaidimas
                    game_over = False
                    player_lives = 5
                    coins_collected = 0
                    caught_count = 0
                    current_level = 1
                    spots_completed = 0
                    show_dugnas = False
                    current_fishing_spot = None
                    fishing_spots.clear()
                    fishing_spots.append(FishingSpot(WIDTH // 2 - 100, HEIGHT // 2 + 150))
                    scroll_x = 0
                    player.x = (WIDTH - FRAME_WIDTH * SCALE) // 2
                    pygame.time.wait(200)  # Trumpa pauzė, kad nepaspautų du kartus
                elif quit_btn.collidepoint(mx, my):
                    running = False
            
            pygame.display.flip()
            clock.tick(60)
            continue
        
        # --- MENIU (PAUZĖ) ---
        if show_menu:
            screen.fill((0, 0, 0))
            
            if show_dugnas:
                # Povandeninis meniu
                buy_btn_rect = ui.draw_menu(screen, show_menu, True, player_lives, coins_collected)
            else:
                # Paviršiaus meniu - naudoti tinkamą foną pagal lygį
                current_bg, current_bg_width = get_current_background(assets, current_level)
                draw_bg_tiled(screen, current_bg, current_bg_width, scroll_x)
                buy_btn_rect = ui.draw_menu(screen, show_menu, False, player_lives, coins_collected)
            
            # Pirkimo logika
            if buy_btn_rect and pygame.mouse.get_pressed()[0]:
                mx, my = pygame.mouse.get_pos()
                if buy_btn_rect.collidepoint(mx, my):
                    player_lives = min(player_lives + 1, MAX_LIVES)
                    coins_collected -= COST_PER_LIFE
            
            pygame.display.flip()
            clock.tick(60)
            continue
        
        # --- POVANDENINIS ŽAIDIMAS ---
        if show_dugnas:
            keys = pygame.key.get_pressed()
            
            # Atnaujinti povandeninį žaidimą
            underwater_game.update(keys)
            
            # Surinkti monetas
            coins_collected += underwater_game.collect_coins()
            
            # Tikrinti kolizijas su rykliais
            player_lives, player_invuln_until, hit = underwater_game.check_shark_collision(
                player_lives, player_invuln_until
            )
            
            if hit and player_lives <= 0:
                # Žaidėjas mirė - Game Over
                game_over = True
                show_dugnas = False
                current_fishing_spot = None
            
            # Nupiešti povandeninį žaidimą
            underwater_game.draw(screen)
            
            # HUD
            ui.draw_caught_fish(screen, underwater_game.caught_count)
            ui.draw_coins(screen, coins_collected)
            ui.draw_lives(screen, player_lives)
            
            # Grįžti į paviršių
            if keys[pygame.K_RETURN]:
                if not underwater_game.can_return():
                    ui.draw_return_warning(screen)
                else:
                    # Pašalinti žvejybos tašką, jei visos žuvys pagautos
                    if current_fishing_spot is not None:
                        current_fishing_spot.disabled = True
                        spots_completed += 1  # Skaičiuoti užbaigtus telkinius
                    
                    # Atnaujinti bendrą pagautų žuvų skaičių
                    caught_count = underwater_game.caught_count
                    
                    # Tikrinti ar reikia pereiti į kitą lygį
                    if spots_completed >= SPOTS_PER_LEVEL and current_level == 1:
                        current_level = 2
                        spots_completed = 0
                        show_level_message = True
                        level_transition_timer = pygame.time.get_ticks()
                        # Reset fishing spots naujam lygiui
                        fishing_spots.clear()
                        fishing_spots.append(FishingSpot(WIDTH // 2 - 100, HEIGHT // 2 + 150))
                        # Reset scroll poziciją
                        scroll_x = 0
                        player.x = (WIDTH - FRAME_WIDTH * SCALE) // 2
                    
                    show_dugnas = False
                    current_fishing_spot = None
            
            pygame.display.flip()
            clock.tick(60)
            continue
        
        # --- PAVIRŠIAUS ŽAIDIMAS ---
        keys = pygame.key.get_pressed()
        
        # Atnaujinti žaidėją
        can_scroll = WORLD_WIDTH > WIDTH
        scroll_x = player.update(keys, scroll_x, can_scroll)
        
        # Clamp scroll
        if can_scroll:
            scroll_x = max(min(scroll_x, 0), -(WORLD_WIDTH - WIDTH))
        else:
            scroll_x = 0
        
        # Atnaujinti varnas
        for varna in varnas:
            varna.update()
        
        # Animacijų atnaujinimas
        varna_anim_frame = (varna_anim_frame + 0.1) % VARNA_NUM_FRAMES
        zuvys_anim_frame = (zuvys_anim_frame + 0.03) % ZUVYS_NUM_FRAMES
        
        # Užtikrinti žvejybos vietą priekyje
        cat_world_x = player.get_world_x(scroll_x)
        ensure_surface_spot_ahead(fishing_spots, cat_world_x)
        
        # Rasti artimiausią žvejybos tašką
        cat_center_x, cat_center_y = player.get_center(scroll_x)
        nearest_fish = None
        nearest_dist = 99999
        
        for spot in fishing_spots:
            if spot.disabled:
                continue
            
            fish_center_x, fish_center_y = spot.get_center()
            dist = ((cat_center_x - fish_center_x)**2 + (cat_center_y - fish_center_y)**2)**0.5
            
            if dist < nearest_dist:
                nearest_dist = dist
                nearest_fish = spot
        
        near_fish = (nearest_dist <= PROXIMITY_THRESHOLD)
        
        # Pradėti žvejybą
        if e_pressed and near_fish and not casting:
            casting = True
            uzmesti_anim_frame = 0.0
        
        # --- PIEŠIMAS ---
        screen.fill((0, 0, 0))
        
        # Nupiešti tinkamą foną pagal lygį
        current_bg, current_bg_width = get_current_background(assets, current_level)
        draw_bg_tiled(screen, current_bg, current_bg_width, scroll_x)
        
        # Piešti varnas
        for varna in varnas:
            varna_frame = assets['varna_frames'][int(varna_anim_frame)]
            varna.draw(screen, varna_frame, scroll_x)
        
        # Piešti žvejybos taškus
        for spot in fishing_spots:
            zuvys_frame = assets['zuvys_frames'][int(zuvys_anim_frame)]
            spot.draw(screen, zuvys_frame, scroll_x)
        
        # Piešti žaidėją (išskyrus žvejojant)
        if not casting:
            player.draw(screen)
        
        # HUD
        ui.draw_caught_fish(screen, caught_count)
        ui.draw_coins(screen, coins_collected)
        ui.draw_lives(screen, player_lives)
        
        # Lygio pranešimas
        if show_level_message:
            elapsed = pygame.time.get_ticks() - level_transition_timer
            if elapsed < 3000:  # Rodyti 3 sekundes
                level_font = pygame.font.SysFont('Arial', 72, bold=True)
                level_text = level_font.render(f"LYGIS {current_level}!", True, (255, 255, 0))
                level_rect = level_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                
                # Šešėlis
                shadow_text = level_font.render(f"LYGIS {current_level}!", True, (0, 0, 0))
                shadow_rect = shadow_text.get_rect(center=(WIDTH // 2 + 4, HEIGHT // 2 + 4))
                screen.blit(shadow_text, shadow_rect)
                screen.blit(level_text, level_rect)
            else:
                show_level_message = False
        
        # Press-E užrašas
        if near_fish and not casting and assets['press_e_frames']:
            press_frame = assets['press_e_frames'][int(press_e_anim_frame) % len(assets['press_e_frames'])]
            ui.draw_press_e_prompt(screen, (nearest_fish.x, nearest_fish.y), scroll_x, press_frame)
            press_e_anim_frame = (press_e_anim_frame + 0.15) % len(assets['press_e_frames'])
        
        # Casting animacija
        if casting and assets['uzmesti_frames']:
            idx = int(uzmesti_anim_frame)
            
            if idx >= len(assets['uzmesti_frames']):
                # Užbaigta - pradėti povandeninį žaidimą
                casting = False
                uzmesti_anim_frame = 0.0
                
                # Kabliuko pozicija
                HAND_REL_X_RIGHT = 0.5
                HAND_REL_X_LEFT = 0.5
                HAND_REL_Y = 0.5
                
                if player.facing_left:
                    hand_x = player.x + int(HAND_REL_X_LEFT * FRAME_WIDTH * SCALE)
                else:
                    hand_x = player.x + int(HAND_REL_X_RIGHT * FRAME_WIDTH * SCALE)
                hand_y = player.y + int(HAND_REL_Y * FRAME_HEIGHT * SCALE)
                
                # Inicializuoti povandeninį žaidimą
                current_fishing_spot = nearest_fish
                underwater_game.initialize(hand_x, hand_y)
                show_dugnas = True
            else:
                # Piešti casting animaciją
                uz_frame = assets['uzmesti_frames'][idx]
                
                if player.facing_left:
                    uz_frame = pygame.transform.flip(uz_frame, True, False)
                
                HAND_REL_X_RIGHT = 0.5
                HAND_REL_X_LEFT = 0.5
                HAND_REL_Y = 0.5
                
                if player.facing_left:
                    hand_x = player.x + int(HAND_REL_X_LEFT * FRAME_WIDTH * SCALE)
                else:
                    hand_x = player.x + int(HAND_REL_X_RIGHT * FRAME_WIDTH * SCALE)
                hand_y = player.y + int(HAND_REL_Y * FRAME_HEIGHT * SCALE)
                
                cast_x = hand_x - uz_frame.get_width() // 2
                cast_y = hand_y - uz_frame.get_height() // 2
                
                screen.blit(uz_frame, (int(cast_x), int(cast_y)))
                uzmesti_anim_frame += 0.4
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()


if __name__ == "__main__":
    main()
