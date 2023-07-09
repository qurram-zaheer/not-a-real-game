import pygame
from settings import *
from os import walk, path
from util import import_folder

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites, create_attack, destroy_attack) -> None:
        super().__init__(groups)
        self.image = pygame.transform.scale(pygame.image.load('../graphics/test/player.png').convert_alpha(), (64,64))
        self.rect = self.image.get_rect(topleft = (pos))
        self.hitbox = self.rect.inflate(0,-25)
        
        # state
        self.status = 'down'
        self.frame_idx = 0
        self.animation_speed = 0.15
        
        # animation asset setup
        self.import_player_assets()
        
        # movement and cooldowns
        self.direction = pygame.math.Vector2()
        self.speed = 5
        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = None
        
        # weapon
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.weapon_idx = 0
        self.weapon = list(weapon_data.keys())[self.weapon_idx]
        self.can_switch_weapon = True
        self.weapon_switch_time = None
        self.switch_duration_cooldown = 200
        
        self.obstacle_sprites = obstacle_sprites

    def import_player_assets(self):
        asset_path = '../graphics/player'
        self.animations = {
            'up': [], 'down': [], 'left': [], 'right': [],
            'up_idle': [], 'down_idle': [], 'left_idle': [], 'right_idle': [],
            'up_attack': [], 'down_attack': [], 'left_attack': [], 'right_attack': []
        }
        
        for animation_key in self.animations.keys():
            frame_path = path.join(asset_path, animation_key)
            self.animations[animation_key] = import_folder(frame_path)
         
    def input(self):
        if not self.attacking:
            keys = pygame.key.get_pressed()
            
            # movement
            if keys[pygame.K_UP]:
                self.status = 'up'
                self.direction.y = -1
            elif keys[pygame.K_DOWN]:
                self.status = 'down'
                self.direction.y = 1
            else:
                self.direction.y = 0
                
            if keys[pygame.K_RIGHT]:
                self.status = 'right'
                self.direction.x = 1
            elif keys[pygame.K_LEFT]:
                self.status = 'left'
                self.direction.x = -1
            else:
                self.direction.x = 0
                
            # melee
            if keys[pygame.K_SPACE]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                self.create_attack()
            
            # cast
            if keys[pygame.K_LCTRL]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                print('cast')
                
            # switch weapon
            if keys[pygame.K_LSHIFT] and self.can_switch_weapon:
                self.can_switch_weapon = False
                self.weapon_switch_time = pygame.time.get_ticks()
                if self.weapon_idx < len(list(weapon_data.keys())) - 1:
                    self.weapon_idx += 1
                else:
                    self.weapon_idx = 0
                self.weapon = list(weapon_data.keys())[self.weapon_idx]
    
    def get_status(self):
        if self.direction.x == 0 and self.direction.y == 0:
            if not 'idle' in self.status and not 'attack' in self.status:
                self.status = self.status + '_idle'
            
        if self.attacking:
            self.direction.x = 0
            self.direction.y = 0
            if not 'attack' in self.status:
                if 'idle' in self.status:
                    self.status = self.status.replace('_idle', '_attack')
                else:
                    self.status = self.status + '_attack'
        else:
            if 'attack' in self.status:
                self.status = self.status.replace('_attack', '')

    def move(self, speed):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
            
        self.hitbox.x += self.direction.x*speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y*speed
        self.collision('vertical')
        
        self.rect.center = self.hitbox.center
        
    def collision(self, direction):
        if direction == 'horizontal':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0: # right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0: # left
                        self.hitbox.left = sprite.hitbox.right
                          
        if direction == 'vertical':
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0: # down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0: # up
                        self.hitbox.top = sprite.hitbox.bottom
            
    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.attacking = False
                self.destroy_attack()
        
        if not self.can_switch_weapon:
            if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
                self.can_switch_weapon = True
                self.destroy_attack()
        
        
    def animate(self):
        animation = self.animations[self.status]
        
        # loop over frame idx
        self.frame_idx += self.animation_speed
        if self.frame_idx > len(animation):
            self.frame_idx = 0
        
        # set the frame img
        self.image = animation[int(self.frame_idx)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

    def update(self):
        self.input()
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.speed)