import pygame
from settings import *
from tile import Tile
from player import Player
from debug import debug
from util import import_csv_layout, import_folder
from random import choice
from weapon import Weapon

class Level:
    def __init__(self) -> None:
        
        # initialize sprite groups
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()
        
        # stripe setup
        self.create_map()
        
        # attack sprites
        self.current_attack = None
        
    def create_map(self):
        layouts = {
            'boundary': import_csv_layout('../map/map_FloorBlocks.csv'),
            'grass': import_csv_layout('../map/map_Grass.csv'),
            'object': import_csv_layout('../map/map_Objects.csv')
        }
        graphics = {
            'grass': import_folder('../graphics/grass'),
            'object': import_folder('../graphics/objects')
        }
        
        for style, layout in layouts.items():
            for row_idx, row in enumerate(layout):
                for col_idx, col in enumerate(row):
                    if col != '-1':
                        x = col_idx*TILESIZE
                        y = row_idx*TILESIZE 
                         
                        if style == 'boundary':
                            Tile((x, y), [self.obstacle_sprites], 'invisible')
                        
                        if style == 'grass':
                            Tile((x,y), [self.visible_sprites, self.obstacle_sprites], 'visible', choice(graphics['grass']))
                        
                        if style == 'object':
                            surf = graphics['object'][int(col)]
                            Tile((x,y), [self.visible_sprites, self.obstacle_sprites], 'object', surf)
                            
        self.player = Player((2000,1430), [self.visible_sprites], self.obstacle_sprites, self.create_attack, self.destroy_attack)
           
        pygame.display.flip()
          
    def create_attack(self):
        self.current_attack = Weapon(self.player, [self.visible_sprites])
    
    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None
    
    def run(self) -> None:
        self.visible_sprites.draw_camera(self.player)
        self.visible_sprites.update()
        debug(self.player.status)
        
class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self) -> None:
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1 ] // 2
        self.camera_offset = pygame.math.Vector2()
        
        # creating the floor
        self.floor_surface = pygame.image.load('../graphics/tilemap/ground.png').convert()
        self.floor_rect = self.floor_surface.get_rect(topleft=(0,0))
        
    def draw_camera(self, player):
        
        # getting the offset
        self.camera_offset.x = player.rect.centerx - self.half_width
        self.camera_offset.y = player.rect.centery - self.half_height
        
        # drawing the floor
        floor_offset_pos = self.floor_rect.topleft - self.camera_offset
        self.display_surface.blit(self.floor_surface, floor_offset_pos)
        
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft -  self.camera_offset
            self.display_surface.blit(sprite.image, offset_pos)
        