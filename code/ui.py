import pygame
from settings import *

class UI:
    def __init__(self) -> None:
        
        # general setup
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
        
        # bar setup
        self.health_bar_rect = pygame.Rect(10,10,HEALTH_BAR_WIDTH,BAR_HEIGHT)
        self.stamina_bar_rect = pygame.Rect(10,34,ENERGY_BAR_WIDTH,BAR_HEIGHT)
        
        # convert weapon dict
        self.weapon_graphics = []
        for weapon in weapon_data.values():
            weapon = pygame.image.load(weapon['graphic']).convert_alpha()
            self.weapon_graphics.append(weapon)
            
        # convert cast dict
        self.weapon_graphics = []
        for weapon in weapon_data.values():
            weapon = pygame.image.load(weapon['graphic']).convert_alpha()
            self.weapon_graphics.append(weapon)
            
        # convert magic dict
        self.cast_graphics = []
        for cast in magic_data.values():
            cast = pygame.image.load(cast['graphic']).convert_alpha()
            self.cast_graphics.append(cast)
        
    def show_bar(self, curr, max, bg_rect, color):
        # draw bg
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
        
        # stat to pixel conversion
        ratio = curr/max
        curr_width = bg_rect.width * ratio
        curr_rect = bg_rect.copy()
        curr_rect.width = curr_width
        
        # draw bar
        pygame.draw.rect(self.display_surface, color, curr_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)
        
    def show_exp(self, exp):
        text_surf = self.font.render(str(int(exp)), False, TEXT_COLOR)
        x = self.display_surface.get_size()[0] - 20
        y =self.display_surface.get_size()[1] - 20
        text_rect = text_surf.get_rect(bottomright=(x,y))
        
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, text_rect.inflate(20,20))
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, text_rect.inflate(20,20), 3)
        self.display_surface.blit(text_surf, text_rect)
    
    def selection_box(self, left, top, has_switched):
        bg_rect = pygame.Rect(left, top, ITEM_BOX_SIZE, ITEM_BOX_SIZE)
        
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, bg_rect)
        
        if has_switched:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR_ACTIVE, bg_rect, 3)
        else:
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 3)
        return bg_rect
    
    def weapon_overlay(self, weapon_idx, has_switched):
        bg_rect = self.selection_box(10,630, has_switched=has_switched)
        weapon_surf = self.weapon_graphics[weapon_idx]
        weapon_rect = weapon_surf.get_rect(center=bg_rect.center)
        self.display_surface.blit(weapon_surf, weapon_rect)
        
    def cast_overlay(self, cast_idx, has_switched):
        bg_rect = self.selection_box(80, 635, has_switched=has_switched)
        cast_surf = self.cast_graphics[cast_idx]
        cast_rect = cast_surf.get_rect(center=bg_rect.center)
        self.display_surface.blit(cast_surf, cast_rect)
    
    def display(self, player):
        self.show_bar(player.health, player.stats['health'], self.health_bar_rect, HEALTH_COLOR)
        self.show_bar(player.stamina, player.stats['stamina'], self.stamina_bar_rect, ENERGY_COLOR)
        
        self.show_exp(player.exp)
        
        self.weapon_overlay(player.weapon_idx, not player.can_switch_weapon)
        self.cast_overlay(player.cast_idx, not player.can_switch_cast)
        # self.selection_box(80,635) # cast