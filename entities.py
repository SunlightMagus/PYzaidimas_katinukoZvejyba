"""
Žaidimo objektai ir jų valdymas (žaidėjas, varnos, žuvys, rykliai)
"""
import pygame
import random
import math
from constants import *


class Player:
    """Žaidėjas (valtis)"""
    def __init__(self, frames):
        self.frames = frames
        self.x = (WIDTH - FRAME_WIDTH * SCALE) // 2
        self.y = (HEIGHT - FRAME_HEIGHT * SCALE) // 2 + 100
        self.current_frame = 0
        self.facing_left = False
        self.moving = False
        self.speed = SPEED
    
    def update(self, keys, scroll_x, can_scroll):
        """Atnaujina žaidėjo poziciją"""
        self.moving = False
        old_x = self.x
        
        if keys[pygame.K_a]:
            self.facing_left = True
            self.moving = True
            if self.x > LEFT_MARGIN or not can_scroll or scroll_x == 0:
                self.x -= self.speed
            elif can_scroll and scroll_x < 0:
                scroll_x += self.speed
        elif keys[pygame.K_d]:
            self.facing_left = False
            self.moving = True
            if self.x < RIGHT_MARGIN or not can_scroll or scroll_x == -(WORLD_WIDTH - WIDTH):
                self.x += self.speed
            elif can_scroll and scroll_x > -(WORLD_WIDTH - WIDTH):
                scroll_x -= self.speed
        
        # Clamp
        self.x = max(0, min(self.x, WIDTH - FRAME_WIDTH * SCALE))
        
        # Animacija
        if self.moving:
            self.current_frame = (self.current_frame + 0.2) % NUM_FRAMES
        else:
            self.current_frame = 0
        
        return scroll_x
    
    def draw(self, screen):
        """Nupiešia žaidėją"""
        frame = self.frames[int(self.current_frame)]
        if self.facing_left:
            frame = pygame.transform.flip(frame, True, False)
        screen.blit(frame, (self.x, self.y))
    
    def get_world_x(self, scroll_x):
        """Grąžina žaidėjo poziciją pasaulio koordinatėse"""
        return self.x - scroll_x
    
    def get_center(self, scroll_x):
        """Grąžina žaidėjo centro koordinates"""
        world_x = self.get_world_x(scroll_x)
        center_x = world_x + (FRAME_WIDTH * SCALE) / 2
        center_y = self.y + (FRAME_HEIGHT * SCALE) / 2
        return center_x, center_y


class Varna:
    """Varnos (paukščiai)"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = random.choice([-1, 1]) * random.uniform(0.5, 1.5)
        self.dy = random.choice([-1, 1]) * random.uniform(0.2, 0.7)
    
    def update(self):
        """Atnaujina varnos poziciją"""
        self.x += self.dx
        self.y += self.dy
        
        # Atsimušti nuo ekrano kraštų
        if self.x < 0 or self.x > WIDTH - VARNA_FRAME_WIDTH * VARNA_SCALE:
            self.dx *= -1
        if self.y < 0 or self.y > 300:
            self.dy *= -1
    
    def draw(self, screen, frame, scroll_x):
        """Nupiešia varną"""
        screen.blit(frame, (int(self.x + scroll_x), int(self.y)))


class FishingSpot:
    """Žvejybos taškas"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.disabled = False
    
    def draw(self, screen, frame, scroll_x):
        """Nupiešia žvejybos tašką"""
        if not self.disabled:
            screen.blit(frame, (int(self.x + scroll_x), self.y))
    
    def get_center(self):
        """Grąžina taško centro koordinates"""
        center_x = self.x + (ZUVYS_FRAME_WIDTH * ZUVYS_SCALE) / 2
        center_y = self.y + (ZUVYS_FRAME_HEIGHT * ZUVYS_SCALE) / 2
        return center_x, center_y


class UnderwaterFish:
    """Povandenė žuvis (gaudoma)"""
    def __init__(self, zuvis_a_img):
        self.x = random.randint(100, WIDTH - 100)
        self.y = random.randint(HEIGHT//2 + 20, HEIGHT - 120)
        self.dx = random.choice([-1, 1]) * random.uniform(1.0, 2.2)
        self.rect = pygame.Rect(self.x, self.y, zuvis_a_img.get_width(), zuvis_a_img.get_height())
        self.frame_idx = 0
        self.frame_tick = 0
        self.caught = False
    
    def update(self, platforms, zuvis_a_frames):
        """Atnaujina žuvies poziciją"""
        self.x += self.dx
        
        # Atsimušti nuo ekrano kraštų
        if self.x <= 10 or self.x >= WIDTH - self.rect.width - 10:
            self.dx *= -1
        
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        # Kolizija su platformomis
        for plat in platforms:
            if self.rect.colliderect(plat):
                if self.rect.centery > plat.top + PLATFORM_TOP_COLLIDE_H:
                    if self.rect.centerx < plat.centerx and self.rect.right > plat.left:
                        self.x = plat.left - self.rect.width
                    elif self.rect.centerx >= plat.centerx and self.rect.left < plat.right:
                        self.x = plat.right
                    self.dx *= -1
                    self.rect.x = int(self.x)
                    break
        
        # Animacija
        if zuvis_a_frames:
            self.frame_tick += 1
            if self.frame_tick >= 8:
                self.frame_tick = 0
                self.frame_idx = (self.frame_idx + 1) % len(zuvis_a_frames)
    
    def draw(self, screen, zuvis_a_frames, zuvis_a_img):
        """Nupiešia žuvį"""
        if zuvis_a_frames:
            img = zuvis_a_frames[self.frame_idx]
        else:
            img = zuvis_a_img
        
        if self.dx < 0:
            img = pygame.transform.flip(img, True, False)
        
        screen.blit(img, (int(self.x), int(self.y)))


class Shark:
    """Ryklys (priešas)"""
    def __init__(self, riklys_a_frames):
        self.x = random.randint(200, 1000)
        self.y = random.randint(HEIGHT // 2 + 10, HEIGHT - 120)
        self.dx = random.choice([-1, 1]) * SHARK_PATROL_SPEED
        self.state = "patrol"
        self.frame_idx = 0
        self.frame_tick = 0
        
        if riklys_a_frames:
            w = riklys_a_frames[0].get_width()
            h = riklys_a_frames[0].get_height()
        else:
            w, h = 32, 16
        
        self.rect = pygame.Rect(self.x, self.y, w, h)
        self.slow_until = 0
    
    def update(self, player_x, player_y, riklys_a_frames, riklys_b_frames):
        """Atnaujina ryklio poziciją ir būseną"""
        now_ms = pygame.time.get_ticks()
        slow_active = now_ms < self.slow_until
        speed_factor = 0.5 if slow_active else 1.0
        
        # Atstumas iki žaidėjo
        dxp = (player_x - self.x)
        dyp = (player_y - self.y)
        dist = (dxp * dxp + dyp * dyp) ** 0.5
        
        # Būsenos sprendimas
        if dist <= SHARK_ATTACK_RANGE:
            self.state = "attack"
            norm = dist if dist != 0 else 1
            self.dx = (dxp / norm) * (SHARK_ATTACK_SPEED * speed_factor)
            self.y += (dyp / norm) * (0.6 * speed_factor)
        else:
            if self.state != "patrol":
                self.state = "patrol"
                self.dx = random.choice([-1, 1]) * (SHARK_PATROL_SPEED * speed_factor)
            
            if random.random() < SHARK_PATROL_TURN_CHANCE:
                self.dx = -self.dx
            
            self.y += math.sin(pygame.time.get_ticks() / 600.0 + self.x) * 0.2
        
        if self.state == "patrol":
            self.dx = math.copysign(SHARK_PATROL_SPEED * speed_factor, self.dx)
        
        # Judėjimas
        self.x += self.dx
        if self.x < 10:
            self.x = 10
            self.dx *= -1
        if self.x > WIDTH - self.rect.width - 10:
            self.x = WIDTH - self.rect.width - 10
            self.dx *= -1
        
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        # Animacija
        self.frame_tick += 1
        if self.frame_tick >= 8:
            self.frame_tick = 0
            self.frame_idx = (self.frame_idx + 1) % RIKLYS_SHEET_FRAMES
    
    def draw(self, screen, riklys_a_frames, riklys_b_frames, uw_scroll_x):
        """Nupiešia ryklį"""
        if self.state == "attack":
            img = riklys_b_frames[self.frame_idx % len(riklys_b_frames)]
        else:
            img = riklys_a_frames[self.frame_idx % len(riklys_a_frames)]
        
        if self.dx < 0:
            img = pygame.transform.flip(img, True, False)
        
        screen.blit(img, (int(self.x - uw_scroll_x), int(self.y)))


class Bubble:
    """Burbulas (sulėtina ryklius)"""
    def __init__(self, x, y, facing_left, burbulai_frames):
        self.x = float(x)
        self.y = float(y)
        self.vx = -BUBBLE_SPEED if facing_left else BUBBLE_SPEED
        self.vy = -0.5
        self.born_ms = pygame.time.get_ticks()
        self.frame_idx = 0
        self.frame_tick = 0
        
        bw = burbulai_frames[0].get_width()
        bh = burbulai_frames[0].get_height()
        self.rect = pygame.Rect(int(x), int(y), bw, bh)
    
    def update(self):
        """Atnaujina burbulo poziciją"""
        self.frame_tick += 1
        if self.frame_tick >= 4:
            self.frame_tick = 0
            self.frame_idx = (self.frame_idx + 1)
        
        self.x += self.vx
        self.y += self.vy
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
    
    def is_expired(self):
        """Patikrina ar burbulas pasenęs"""
        return pygame.time.get_ticks() - self.born_ms >= BUBBLE_LIFETIME_MS
    
    def draw(self, screen, burbulai_frames, uw_scroll_x):
        """Nupiešia burbulą"""
        img_b = burbulai_frames[self.frame_idx % len(burbulai_frames)]
        screen.blit(img_b, (int(self.x - uw_scroll_x), int(self.y)))


class Coin:
    """Moneta (surenkama povandeniniame žaidime)"""
    def __init__(self, x, y, coin_frames):
        self.x = x
        self.y = y
        self.frame_idx = 0
        self.frame_tick = 0
        
        cw = coin_frames[0].get_width()
        ch = coin_frames[0].get_height()
        self.rect = pygame.Rect(x, y, cw, ch)
    
    def update(self):
        """Atnaujina monetos animaciją"""
        self.frame_tick += 1
        if self.frame_tick >= 6:
            self.frame_tick = 0
            self.frame_idx = (self.frame_idx + 1)
    
    def draw(self, screen, coin_frames, uw_scroll_x):
        """Nupiešia monetą"""
        coin_img = coin_frames[self.frame_idx % len(coin_frames)]
        screen.blit(coin_img, (int(self.x - uw_scroll_x), int(self.y)))
