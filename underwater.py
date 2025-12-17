"""
Povandeninis žaidimas (mini-žaidimas žvejybos metu)
"""
import pygame
import random
from constants import *
from entities import UnderwaterFish, Shark, Bubble, Coin


class UnderwaterGame:
    """Povandeninio žaidimo logika"""
    def __init__(self, assets, sounds):
        self.assets = assets
        self.sounds = sounds
        
        # Žaidėjo būsena
        self.player_x = WIDTH // 2
        self.player_y = 80
        self.player_vy = 0.0
        self.facing_left = False
        
        # Kameros offset
        self.scroll_x = 0
        
        # Objektai
        self.fish = []
        self.sharks = []
        self.bubbles = []
        self.coins = []
        self.platforms = []
        
        # Kabliukas (kur žvejyba prasidėjo)
        self.hook_x = None
        self.hook_y = None
        
        # Burbulų cooldown
        self.last_bubble_ms = 0
        
        # Statistika
        self.caught_count = 0
    
    def spawn_fish(self, n=6):
        """Sukuria povandenes žuvis"""
        self.fish.clear()
        for _ in range(n):
            fish = UnderwaterFish(self.assets['zuvis_a_img'])
            self.fish.append(fish)
    
    def spawn_sharks(self, n=2, x_min=200, x_max=1000):
        """Sukuria ryklius"""
        self.sharks.clear()
        for _ in range(n):
            shark = Shark(self.assets['riklys_a_frames'])
            shark.x = random.randint(x_min, x_max)
            shark.y = random.randint(HEIGHT // 2 + 10, HEIGHT - 120)
            self.sharks.append(shark)
    
    def spawn_platforms(self):
        """Sukuria platformas"""
        self.platforms.clear()
        pw = self.assets['platform_img'].get_width()
        ph = self.assets['platform_img'].get_height()
        for px, py in [(300, HEIGHT//2 + 40), (860, HEIGHT//2 + 70)]:
            self.platforms.append(pygame.Rect(px, py, pw, ph))
    
    def spawn_coins(self):
        """Sukuria monetas"""
        self.coins.clear()
        if self.assets['coin_frames']:
            cw = self.assets['coin_frames'][0].get_width()
            ch = self.assets['coin_frames'][0].get_height()
            for cx, cy in [(300 + self.assets['platform_img'].get_width() // 2, HEIGHT//2 + 10),
                          (860 + self.assets['platform_img'].get_width() // 2, HEIGHT//2 + 20)]:
                coin = Coin(cx, cy, self.assets['coin_frames'])
                self.coins.append(coin)
    
    def initialize(self, hook_x, hook_y):
        """Inicializuoja povandeninį žaidimą"""
        self.hook_x = hook_x
        self.hook_y = hook_y
        
        self.player_x = hook_x if hook_x is not None else WIDTH // 2
        self.player_y = max(30, int(hook_y + 10))
        self.player_vy = 0.0
        
        self.spawn_fish(6)
        
        # Rykliai šalia kabliuko
        sx_min = int(hook_x + 60) if hook_x else 200
        sx_max = int(hook_x + 400) if hook_x else 800
        self.spawn_sharks(n=2, x_min=sx_min, x_max=sx_max)
        
        self.spawn_platforms()
        self.spawn_coins()
    
    def update_player(self, keys):
        """Atnaujina žaidėjo poziciją ir fiziką"""
        player_w = self.assets['blizge_img'].get_width()
        player_h = self.assets['blizge_img'].get_height()
        
        prev_x, prev_y = self.player_x, self.player_y
        
        # Horizontalus judėjimas
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.player_x -= UW_SPEED
            self.facing_left = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.player_x += UW_SPEED
            self.facing_left = False
        
        # Plaukimas aukštyn
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.player_vy = -5.5
        
        # Gravitacija
        self.player_vy += GRAVITY
        self.player_y += self.player_vy
        
        # Ribos
        self.player_x = max(0 + player_w // 2, min(self.player_x, WIDTH - player_w // 2))
        bottom_y = HEIGHT - player_h - 10
        if self.player_y >= bottom_y:
            self.player_y = bottom_y
            self.player_vy = 0.0
        
        # Kolizija su platformomis
        p_rect = pygame.Rect(int(self.player_x - player_w // 2), int(self.player_y), player_w, player_h)
        prev_rect = pygame.Rect(int(prev_x - player_w // 2), int(prev_y), player_w, player_h)
        
        for plat in self.platforms:
            plat_top = pygame.Rect(plat.x, plat.y, plat.width, max(28, PLATFORM_TOP_COLLIDE_H))
            
            crossing_top = (
                self.player_vy > 0 and
                prev_rect.bottom <= plat_top.top and
                p_rect.bottom >= plat_top.top and
                p_rect.centerx >= plat.left and p_rect.centerx <= plat.right
            )
            
            if crossing_top:
                self.player_y = plat_top.top - player_h
                self.player_vy = 0.0
                p_rect.y = int(self.player_y)
                continue
            
            if p_rect.colliderect(plat) and p_rect.bottom > plat_top.top + 2:
                if prev_rect.right <= plat.left and p_rect.right > plat.left:
                    self.player_x = plat.left - player_w // 2
                elif prev_rect.left >= plat.right and p_rect.left < plat.right:
                    self.player_x = plat.right + player_w // 2
                p_rect.x = int(self.player_x - player_w // 2)
    
    def spawn_bubble(self, keys):
        """Sukuria burbulą"""
        now_ms = pygame.time.get_ticks()
        if keys[pygame.K_f] and (now_ms - self.last_bubble_ms) >= BUBBLE_COOLDOWN_MS:
            if self.assets['burbulai_frames']:
                player_w = self.assets['blizge_img'].get_width()
                player_h = self.assets['blizge_img'].get_height()
                
                spawn_x = self.player_x + (-player_w // 2 if self.facing_left else player_w // 2)
                spawn_y = self.player_y + int(player_h * 0.4)
                
                bubble = Bubble(spawn_x, spawn_y, self.facing_left, self.assets['burbulai_frames'])
                self.bubbles.append(bubble)
                self.last_bubble_ms = now_ms
    
    def update_fish(self):
        """Atnaujina žuvis"""
        for fish in self.fish:
            fish.update(self.platforms, self.assets['zuvis_a_frames'])
    
    def update_sharks(self):
        """Atnaujina ryklius"""
        for shark in self.sharks:
            shark.update(self.player_x, self.player_y, 
                        self.assets['riklys_a_frames'], 
                        self.assets['riklys_b_frames'])
    
    def update_bubbles(self):
        """Atnaujina burbulus"""
        for bubble in self.bubbles[:]:
            bubble.update()
            
            # Pašalinti pasenusį
            if bubble.is_expired():
                self.bubbles.remove(bubble)
                continue
            
            # Kolizija su platformomis
            popped = False
            for plat in self.platforms:
                if bubble.rect.colliderect(plat):
                    self.bubbles.remove(bubble)
                    popped = True
                    break
            
            if popped:
                continue
            
            # Kolizija su rykliais - sulėtinti
            for shark in self.sharks:
                if shark.rect.colliderect(bubble.rect):
                    shark.slow_until = pygame.time.get_ticks() + SHARK_SLOW_MS
                    if bubble in self.bubbles:
                        self.bubbles.remove(bubble)
                    break
    
    def update_coins(self):
        """Atnaujina monetas"""
        for coin in self.coins:
            coin.update()
    
    def catch_fish(self, keys):
        """Žaidėjas gaudo žuvį"""
        if keys[pygame.K_SPACE]:
            player_w = self.assets['blizge_img'].get_width()
            player_h = self.assets['blizge_img'].get_height()
            p_rect = pygame.Rect(int(self.player_x - player_w // 2), int(self.player_y), player_w, player_h)
            
            for fish in self.fish[:]:
                if fish.rect.colliderect(p_rect):
                    self.fish.remove(fish)
                    self.caught_count += 1
                    
                    # Garsas
                    if self.sounds['reelin_sound']:
                        try:
                            self.sounds['reelin_sound'].play()
                        except Exception:
                            pass
    
    def collect_coins(self):
        """Renka monetas"""
        player_w = self.assets['blizge_img'].get_width()
        player_h = self.assets['blizge_img'].get_height()
        p_rect = pygame.Rect(int(self.player_x - player_w // 2), int(self.player_y), player_w, player_h)
        
        collected = 0
        for coin in self.coins[:]:
            if p_rect.colliderect(coin.rect):
                self.coins.remove(coin)
                collected += 1
                
                # Garsas
                if self.sounds['coin_sound']:
                    try:
                        self.sounds['coin_sound'].play()
                    except Exception:
                        pass
        
        return collected
    
    def check_shark_collision(self, player_lives, player_invuln_until):
        """Tikrina kolizijas su rykliais"""
        now_ms = pygame.time.get_ticks()
        
        if now_ms >= player_invuln_until:
            player_w = self.assets['blizge_img'].get_width()
            player_h = self.assets['blizge_img'].get_height()
            p_rect = pygame.Rect(int(self.player_x - player_w // 2), int(self.player_y), player_w, player_h)
            p_hit = p_rect.inflate(-int(p_rect.width * 0.4), -int(p_rect.height * 0.4))
            
            for shark in self.sharks:
                s_hit = shark.rect.inflate(-int(shark.rect.width * 0.6), -int(shark.rect.height * 0.6))
                
                if s_hit.colliderect(p_hit):
                    player_lives -= 1
                    
                    # Garsas
                    if self.sounds['hurt_sound']:
                        try:
                            self.sounds['hurt_sound'].play()
                        except Exception:
                            pass
                    
                    player_invuln_until = now_ms + INVULN_MS
                    
                    # Knockback
                    if shark.x < self.player_x:
                        self.player_x += 40
                    else:
                        self.player_x -= 40
                    
                    return player_lives, player_invuln_until, True
        
        return player_lives, player_invuln_until, False
    
    def can_return(self):
        """Ar galima grįžti į paviršių"""
        return len(self.fish) == 0
    
    def update(self, keys):
        """Atnaujina visą povandeninį žaidimą"""
        self.update_player(keys)
        self.spawn_bubble(keys)
        self.update_fish()
        self.update_sharks()
        self.update_bubbles()
        self.update_coins()
        self.catch_fish(keys)
    
    def draw(self, screen):
        """Nupiešia povandeninį žaidimą"""
        # Fonas
        screen.blit(self.assets['dugnas'], (0, 0))
        
        # Platformos
        for plat in self.platforms:
            screen.blit(self.assets['platform_img'], plat.topleft)
        
        # Žuvys
        for fish in self.fish:
            fish.draw(screen, self.assets['zuvis_a_frames'], self.assets['zuvis_a_img'])
        
        # Burbulai
        for bubble in self.bubbles:
            bubble.draw(screen, self.assets['burbulai_frames'], self.scroll_x)
        
        # Monetos
        for coin in self.coins:
            coin.draw(screen, self.assets['coin_frames'], self.scroll_x)
        
        # Rykliai
        for shark in self.sharks:
            shark.draw(screen, self.assets['riklys_a_frames'], 
                      self.assets['riklys_b_frames'], self.scroll_x)
        
        # Žaidėjas
        player_w = self.assets['blizge_img'].get_width()
        blizge_draw = self.assets['blizge_img']
        if self.facing_left:
            blizge_draw = pygame.transform.flip(self.assets['blizge_img'], True, False)
        screen.blit(blizge_draw, (int(self.player_x - player_w // 2), int(self.player_y)))
