from csv import reader
import os
import pygame

def import_csv_layout(path):
    terrain_map = []
    with open(path) as level_map:
        layout = reader(level_map, delimiter=',')
        for row in layout:
            terrain_map.append(list(row))
        return terrain_map

def import_folder(path):
    surface_list = []
    sorted_list = []

    for _, __, img_files in os.walk(path):
        for image in img_files:
            sorted_list.append(image)
        sorted_list.sort()
        for img in sorted_list:            
            full_path = path + "/" + img
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)
    
    return surface_list
            
            