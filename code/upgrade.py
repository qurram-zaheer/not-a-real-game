import pygame
from settings import *

class Upgrade:
    def __init__(self, player) -> None:
        self.display_surface = pygame.display.get_surface()
        self.player = player
        
        self.attr_num = len(self.player.stats)
        self.attr_names = list(self.player.stats.keys())
        self.max_vals = list(self.player.max_stats.values())
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)
        
        # selection system
        self.sel_idx = 0
        self.sel_time = None
        self.can_move = True
        
        # item dims
        self.height = self.display_surface.get_size()[1]*0.8
        self.width = self.display_surface.get_size()[0] // 6
        
        self.create_items()
        
    def input(self):
        keys = pygame.key.get_pressed()
        
        if self.can_move:
            if keys[pygame.K_RIGHT] and self.sel_idx < self.attr_num - 1:
                self.sel_idx += 1
                self.can_move = False
                self.sel_time = pygame.time.get_ticks()
            elif keys[pygame.K_LEFT]and self.sel_idx >= 1:
                self.sel_idx -= 1
                self.can_move = False
                self.sel_time = pygame.time.get_ticks()
            
            if keys[pygame.K_SPACE]:
                self.can_move = False
                self.sel_time = pygame.time.get_ticks()
                self.item_list[self.sel_idx].trigger(self.player)
    
    def sel_cooldown(self):
        if not self.can_move:
            curr_time = pygame.time.get_ticks()
            if curr_time - self.sel_time >= 300:
                self.can_move = True
    
    def create_items(self):
        self.item_list = []
        for i, idx in enumerate(range(self.attr_num)):
            top = self.display_surface.get_size()[1]*0.1
            full_width = self.display_surface.get_size()[0]
            increment = full_width // self.attr_num
            left = (i * increment) + (increment - self.width) // 2
            
            item = Item(left, top, self.width, self.height, idx, self.font)
            self.item_list.append(item)
    
    def display(self):
        self.input()
        self.sel_cooldown()
        
        for idx, item in enumerate(self.item_list):
            
            # get attrs
            name = self.attr_names[idx]
            value = self.player.get_value_by_idx(idx)
            max_value = self.max_vals[idx]
            cost = self.player.get_cost_by_idx(idx)
            item.display(self.display_surface, self.sel_idx, name, value, max_value, cost)
        

class Item:
    def __init__(self, left, top, width, height, idx, font) -> None:
        self.rect = pygame.Rect(left, top, width, height)
        self.idx = idx
        self.font = font
        
    def display_names(self, display_surface, name, cost, selected):
        if selected:
            color = TEXT_COLOR_SELECTED
        else:
            color = TEXT_COLOR
        # title
        title_surf = self.font.render(name, False, color)
        title_rect = title_surf.get_rect(midtop=self.rect.midtop + pygame.math.Vector2(0,20))
        # cost
        cost_surf = self.font.render(str(int(cost)), False, color)
        cost_rect = cost_surf.get_rect(midbottom=self.rect.midbottom + pygame.math.Vector2(0,-20))
        # draw
        display_surface.blit(title_surf, title_rect)
        display_surface.blit(cost_surf, cost_rect)
        
    def display_bar(self, surface, val, max, selected):
        
        # drawing setup
        top = self.rect.midtop + pygame.Vector2(0,60)
        bottom = self.rect.midbottom + pygame.Vector2(0,-60)
        color = BAR_COLOR_SELECTED if selected else BAR_COLOR
        
        # bar setup
        full_height = bottom[1] - top[1]
        rel_num = (val/max) * full_height
        val_rect = pygame.Rect(top[0] - 15, bottom[1] - rel_num, 30, 10)
        
        # draw
        pygame.draw.line(surface, color, top, bottom, 5)
        pygame.draw.rect(surface, color, val_rect)
    
    def trigger(self, player):
        upgrade_attr = list(player.stats.keys())[self.idx]
        if player.exp >= player.upgrade_cost[upgrade_attr] and player.stats[upgrade_attr] < player.max_stats[upgrade_attr]:
            player.exp -= player.upgrade_cost[upgrade_attr]
            player.stats[upgrade_attr] *= 1.2
            player.upgrade_cost[upgrade_attr] *= 1.4
            
        if player.stats[upgrade_attr] > player.max_stats[upgrade_attr]:
            player.stats[upgrade_attr] = player.max_stats[upgrade_attr]
    
    def display(self, display_surface, sel_idx, name, value, max, cost):
        if self.idx == sel_idx:
            pygame.draw.rect(display_surface, UPGRADE_BG_COLOR_SELECTED, self.rect)
        else:
            pygame.draw.rect(display_surface, UI_BG_COLOR, self.rect)
        pygame.draw.rect(display_surface, UI_BORDER_COLOR, self.rect, 4)
        self.display_names(display_surface, name, cost, self.idx == sel_idx)
        
        self.display_bar(display_surface, value, max, self.idx == sel_idx)