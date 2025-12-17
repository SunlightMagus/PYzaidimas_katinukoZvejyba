"""
Vartotojo sąsajos elementai (HUD, meniu, tekstai)
"""
import pygame
from constants import *


class UI:
    """Vartotojo sąsajos valdymas"""
    def __init__(self, assets):
        self.assets = assets
        self.small_font = pygame.font.SysFont('Arial', 24)
        self.menu_font = pygame.font.SysFont('Arial', 32, bold=True)
        self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
    
    def draw_caught_fish(self, screen, caught_count):
        """Nupiešia pagautų žuvų skaičių"""
        icon_x, icon_y = 20, 50
        if self.assets['dead_img']:
            screen.blit(self.assets['dead_img'], (icon_x, icon_y))
            cnt_surf = self.small_font.render(str(caught_count), True, (255, 255, 255))
            screen.blit(cnt_surf, (icon_x + self.assets['dead_img'].get_width() + 8,
                                  icon_y + (self.assets['dead_img'].get_height() - cnt_surf.get_height()) // 2))
        else:
            score = self.small_font.render(f"Pagauta žuvų: {caught_count}", True, (255, 255, 255))
            screen.blit(score, (20, 50))
    
    def draw_coins(self, screen, coins_collected):
        """Nupiešia surinktų monetų skaičių"""
        coin_icon_pos = (20, 120)
        screen.blit(self.assets['pinigas_icon'], coin_icon_pos)
        coins_text = self.small_font.render(str(coins_collected), True, (255, 230, 120))
        screen.blit(coins_text, (coin_icon_pos[0] + self.assets['pinigas_icon'].get_width() + 8,
                                coin_icon_pos[1] + (self.assets['pinigas_icon'].get_height() - coins_text.get_height()) // 2))
    
    def draw_lives(self, screen, player_lives):
        """Nupiešia žaidėjo gyvybes"""
        if self.assets['hp_images']:
            hp_idx = max(0, min(player_lives - 1, len(self.assets['hp_images']) - 1))
            hp_img = self.assets['hp_images'][hp_idx]
            screen.blit(hp_img, (WIDTH - hp_img.get_width() - 20, 20))
        else:
            lives_surf = self.small_font.render(f"Gyvybės: {player_lives}", True, (255, 200, 50))
            screen.blit(lives_surf, (WIDTH - 180, 20))
    
    def draw_press_e_prompt(self, screen, nearest_fish_pos, scroll_x, press_e_frame):
        """Nupiešia 'spausk E' užrašą"""
        prompt_x = nearest_fish_pos[0] + (ZUVYS_FRAME_WIDTH * ZUVYS_SCALE) // 2 - press_e_frame.get_width() // 2 + scroll_x
        prompt_y = nearest_fish_pos[1] - press_e_frame.get_height() - 10
        screen.blit(press_e_frame, (int(prompt_x), int(prompt_y)))
    
    def draw_return_warning(self, screen):
        """Nupiešia įspėjimą, kad negalima grįžti"""
        warn = self.small_font.render("Negalite grįžti — sugaukite visas žuvis", True, (255, 80, 80))
        warn_rect = warn.get_rect(center=(WIDTH // 2, HEIGHT - 80))
        screen.blit(warn, warn_rect)
    
    def draw_menu(self, screen, show_menu, is_underwater, player_lives, coins_collected):
        """Nupiešia meniu su pirkimo mygtuku (veikia ir paviršiuje, ir po vandeniu)"""
        if not show_menu or not self.assets['meniu_img']:
            return None
        
        card_w, card_h = self.assets['meniu_img'].get_size()
        card_x = (WIDTH - card_w) // 2
        card_y = (HEIGHT - card_h) // 2
        screen.blit(self.assets['meniu_img'], (card_x, card_y))
        
        # Pavadinimas
        t_surf = self.title_font.render("Katinuko žvejyba", True, (0, 0, 0))
        t_rect = t_surf.get_rect(midtop=(card_x + card_w // 2, card_y + 18))
        screen.blit(t_surf, t_rect)
        
        # Valdymo instrukcijos
        if is_underwater:
            lines = [
                "Valdymas (po vandeniu):",
                "W/↑ – plaukti aukštyn",
                "A/D – kairė/dešinė",
                "SPACE – gaudyti žuvį",
                "F – burbulai",
                "ENTER – grįžti į paviršių",
                "ESC – tęsti"
            ]
        else:
            lines = [
                "Valdymas (paviršius):",
                "A/D – plaukti kairė/dešinė",
                "E – pradėti žvejybą",
                "ESC – tęsti"
            ]
        
        tx = card_x + 40
        ty = card_y + 90
        for txt in lines:
            surf = self.menu_font.render(txt, True, (0, 0, 0))
            screen.blit(surf, (tx, ty))
            ty += 40
        
        # Pirkimo mygtukas
        btn_w, btn_h = 220, 56
        btn_x = card_x + card_w - btn_w - 40
        btn_y = card_y + card_h - btn_h - 40
        buy_btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        
        can_buy = (player_lives < MAX_LIVES) and (coins_collected >= COST_PER_LIFE)
        bg_color = (60, 200, 80) if can_buy else (150, 150, 150)
        
        pygame.draw.rect(screen, bg_color, buy_btn_rect, border_radius=8)
        pygame.draw.rect(screen, (30, 30, 30), buy_btn_rect, 2, border_radius=8)
        
        # Mygtukas BE kainos
        label = "Pirkti gyvybę"
        lbl_surf = self.menu_font.render(label, True, (0, 0, 0))
        lbl_rect = lbl_surf.get_rect(center=buy_btn_rect.center)
        screen.blit(lbl_surf, lbl_rect)
        
        # Info tekstas
        info_font = pygame.font.SysFont('Arial', 24, bold=False)
        info_text = f"Gyvybės: {player_lives}/{MAX_LIVES} | Monetos: {coins_collected} | Kaina: {COST_PER_LIFE} m."
        info_surf = info_font.render(info_text, True, (0, 0, 0))
        screen.blit(info_surf, (card_x + 40, card_y + card_h - 40 - info_surf.get_height()))
        
        return buy_btn_rect if can_buy else None
