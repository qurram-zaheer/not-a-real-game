import pygame
from settings import *
from os import walk, path
from util import import_folder
from entity import Entity

class Player(Entity):
    def __init__(self, pos, groups, obstacle_sprites, create_attack, destroy_attack, create_cast) -> None:
        super().__init__(groups)
        self.image = pygame.transform.scale(pygame.image.load('../graphics/test/player.png').convert_alpha(), (64,64))
        self.rect = self.image.get_rect(topleft = (pos))
        self.hitbox = self.rect.inflate(0,-25)
        
        # state
        self.status = 'down'
        
        # animation asset setup
        self.import_player_assets()
        
        # movement and cooldowns
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
        
        # casting
        self.create_cast = create_cast
        self.cast_idx = 0
        self.cast = list(magic_data.keys())[self.cast_idx]
        self.can_switch_cast = True
        self.cast_switch_time = None
        
        # stats
        self.stats = {'health': 100, 'stamina': 60, 'attack': 10, 'magic': 4, 'speed': 6}
        self.health = self.stats['health']
        self.stamina = self.stats['stamina']
        self.exp = 0
        self.speed = self.stats['speed']
        
        # receive damage
        self.vulnerable = True
        self.hurt_time = None
        self.invuln_duration = 500
        
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
                style = list(magic_data.keys())[self.cast_idx]
                strength = list(magic_data.values())[self.cast_idx]['strength'] + self.stats['magic']
                cost = list(magic_data.values())[self.cast_idx]['cost']
                self.create_cast(style, strength, cost)
                
            # switch weapon
            if keys[pygame.K_q] and self.can_switch_weapon:
                self.can_switch_weapon = False
                self.weapon_switch_time = pygame.time.get_ticks()
                if self.weapon_idx < len(list(weapon_data.keys())) - 1:
                    self.weapon_idx += 1
                else:
                    self.weapon_idx = 0
                self.weapon = list(weapon_data.keys())[self.weapon_idx]
                
            # switch weapon
            if keys[pygame.K_e] and self.can_switch_cast:
                self.can_switch_cast = False
                self.cast_switch_time = pygame.time.get_ticks()
                if self.cast_idx < len(list(magic_data.keys())) - 1:
                    self.cast_idx += 1
                else:
                    self.cast_idx = 0
                self.cast = list(magic_data.keys())[self.cast_idx]
    
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
            
    def cooldowns(self):
        current_time = pygame.time.get_ticks()
        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown + weapon_data[self.weapon]['cooldown']:
                self.attacking = False
                self.destroy_attack()
        
        if not self.can_switch_weapon:
            if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
                self.can_switch_weapon = True
                
        if not self.can_switch_cast:
            if current_time - self.cast_switch_time >= self.switch_duration_cooldown:
                self.can_switch_cast = True
                
        if not self.vulnerable:
            if current_time - self.hurt_time >= self.invuln_duration:
                self.vulnerable = True
        
    def animate(self):
        animation = self.animations[self.status]
        
        # loop over frame idx
        self.frame_idx += self.animation_speed
        if self.frame_idx > len(animation):
            self.frame_idx = 0
        
        # set the frame img
        self.image = animation[int(self.frame_idx)]
        self.rect = self.image.get_rect(center=self.hitbox.center)
        
        # flicker on hit
        if not self.vulnerable:
            self.image.set_alpha(self.wave_value())
        else:
            self.image.set_alpha(255)

    def stamina_recovery(self):
        if self.stamina < self.stats['stamina']:
            self.stamina += 0.01 * self.stats['magic']
        else:
            self.stamina = self.stats['stamina']
    
    def get_full_weapon_damage(self):
        base_dmg = self.stats['attack']
        weapon_dmg = weapon_data[self.weapon]['damage']
        return base_dmg + weapon_dmg

    def get_full_magic_damage(self):
        base_dmg = self.stats['magic']
        spell_dmg = magic_data[self.cast]['strength']
        
        return base_dmg + spell_dmg
    
    def update(self):
        self.input()
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.speed)
        self.stamina_recovery()