import pygame
from settings import *
from tile import Tile
from player import Player
from debug import debug

class Level:
    def __init__(self) -> None:
        
        # get display surface
        self.display_surface = pygame.display.get_surface()
        
        # initialize sprite groups
        self.visible_sprites = pygame.sprite.Group()
        self.obstacle_sprites = pygame.sprite.Group()
        
        # stripe setup
        self.create_map()
        
    def create_map(self):
        for row_index, row in enumerate(WORLD_MAP):
            for col_index, col in enumerate(row):
                x = col_index*TILESIZE
                y = row_index*TILESIZE
                
                if col == 'x':
                    Tile((x,y), [self.visible_sprites, self.obstacle_sprites])
                
                elif col == 'p':
                    self.player = Player((x,y), [self.visible_sprites])
                    
        
        pygame.display.flip()
            
    
    def run(self) -> None:
        self.visible_sprites.draw(self.display_surface)
        self.visible_sprites.update()
        debug(self.player.direction)