# Standard
import os
import json
import time

#3rd party
import pygame

# Local
from utilities.manager import EntityManager
from utilities.quadtree import QuadTree
from utilities.entities import Player, Remnant, Tile
from utilities.spritesheet import Spritesheet


class LevelInfo:
    __cached_assets = {}

    def __init__(self):
        self.SHOW_ERRORS = False # Displays all exceptions / errors for the purpose of debugging

        # Main levels
        self.current_level = 0
        self.MAX_LEVEL = len( os.listdir(os.getcwd() + f'/world/simplified') ) - 1

        # Side levels
        self.side_level = False
        self.current_side_level = 0

        self.ROOT_PATH = os.getcwd()
        self.TILE_SIZE = self.GRID_SIZE = (16, 16)

        self.map_data = None
        self.static = QuadTree
        self.entities = EntityManager

        self.interactables = None

        self.background = None
        self.foreground = None

        self.COLOURS = {
            1 : (185,185,185), # Wall
            2 : (240,27,27), # Death
            3 : (51,255,255), # Previous
            4 : (76,153,0), # Next
            5 : (204,204,0) # Bounce
        }

        self.ENTITY_DATA = {
            1 : {
                'class' : Player,
                'size' : (14, 26),
                'colour' : (231,238,53),
                'asset' : '/images/player/',
                'fSize' : (192, 192),
                'visual' : True,
                },
            2 : {
                'class' : Remnant,
                'size' : (16, 24),
                'colour' : (153,0,0),
                'asset' : '/images/remnant/small/',
                'fSize' : (92, 36),
                'visual' : True
                },
            3 : {
                'class' : Remnant,
                'size' : (16, 24),
                'colour' : (153,0,0),
                'asset' : '/images/remnant/big/',
                'fSize' : (92, 36),
                'visual' : True
                },
            4 : None
        }


    def load_level(self, progress, game):
        progress.put(0) # 0%

        if self.current_level >= self.MAX_LEVEL:
            return
        
        self.__data()
        progress.put(20) # 20%
        
        self.__tiles()
        progress.put(40) # 40%

        self.__background()
        progress.put(60) # 60%

        self.__entities()
        game.target = self.entities.retr_player()
        game.offset = [[game.target.x + game.target.w / 2, game.target.y + game.target.h / 2][n] - game.res_screen[n] / [2, 1.8][n] for n in range(2)]
        progress.put(80) # 80%

        self.__foreground()
        progress.put(100) # 100%

        game.run_level_sequence = True

        time.sleep(1)
        return

    def __data(self):
        with open(f'world/simplified/Level_{self.current_level}' + '/data.json') as map_data:
            self.map_data = json.load(map_data)

    def __tiles(self):
        # Determines whether to load main level or a side level inside the current main level
        if self.side_level != True:
            with open(f'world/simplified/Level_{self.current_level}' + '/TileGrid.csv', 'r') as csv:
                intGrid = [[int(value) for value in row if value != ','] for row in csv.read().split('\n')]
        else:
            with open(f'world/simplified/Level_{self.current_level}_{self.current_side_level}' + '/TileGrid.csv', 'r') as csv:
                intGrid = [[int(value) for value in row if value != ','] for row in csv.read().split('\n')]

        tiles = []
        for y, row in enumerate(intGrid):
            for x, value in enumerate(row):

                if value != 0:
                    image = self.__cached_lookup(self.TILE_SIZE, self.COLOURS[value])
                    position = (self.map_data['x'] + x * self.TILE_SIZE[0], self.map_data['y'] + y * self.TILE_SIZE[1])

                    tiles.append(Tile(image, position, self.TILE_SIZE, value))

        self.static = QuadTree(tiles)

    def __entities(self):
        with open(f'world/simplified/Level_{self.current_level}' + '/EntityGrid.csv', 'r') as csv:
            intGrid = [[int(value) for value in row if value != ','] for row in csv.read().split('\n')]

        self.entities = EntityManager()

        player, entities = None, []
        for y, row in enumerate(intGrid):
            for x, value in enumerate(row):
                
                if value != 0:
                    entity_data = self.ENTITY_DATA[value]
                    
                    position = (self.map_data['x'] + x * self.GRID_SIZE[0], self.map_data['y'] + y * self.GRID_SIZE[1] - entity_data['size'][1])
                    
                    if entity_data['visual']:
                        assets = self.__cached_lookup(entity_data['size'], entity_data['asset'], entity_data['visual'], entity_data['fSize'])
                    else:
                        assets = self.__cached_lookup(entity_data['size'], entity_data['colour'])

                    if not entity_data['visual']:
                        info = [assets, position, entity_data['size']]
                    else:
                        image = assets['run'][0][0]
                        info = [image, position, entity_data['size'], assets]

                    if value == 1:
                        player = entity_data['class'](*info)
                    else:
                        entities.append(entity_data['class'](*info))

        if player: self.entities.add(player)
        self.entities.add_multiple(entities)

    def __background(self):
        try:
            self.background = pygame.image.load(f'images/background/Level_{self.current_level}/thigh.png').convert_alpha()
        except:
            self.background = None
            if self.SHOW_ERRORS == True:
                print(f'No background found for level {self.current_level}')

    def __foreground(self):
        try:
            self.foreground = pygame.image.load(f'images/foreground/Level_{self.current_level}/thig.png').convert_alpha()
        except:
            self.foreground = None
            if self.SHOW_ERRORS == True:
                print(f'No foreground found for level {self.current_level}')

    def __cached_lookup(self, size, asset, animation=False, frame_size=None, ):

        if not animation:
            cached_lookup = (size, asset)

            if not ( cached_image := self.__cached_assets.get(cached_lookup, None) ):
                cached_image = pygame.Surface(size)
                cached_image.fill(asset)

                self.__cached_assets[cached_lookup] = cached_image

            return cached_image
        
        temp_assets = {}
        FOLDER_PATH = self.ROOT_PATH + asset
        
        for file_path in os.listdir(FOLDER_PATH):
            cached_lookup = (size, asset + file_path)

            file_name = file_path.partition('_')
            
            if not (cached_asset := self.__cached_assets.get(cached_lookup, None)):
                cached_asset = pygame.image.load(FOLDER_PATH + file_path).convert_alpha()

                if 'spritesheet' in file_name[2]:
                    cached_asset = Spritesheet(cached_asset, frame_size).divide_spritesheet((83,83,83))
                else:
                    cached_asset = pygame.transform.scale(cached_asset, size)

                self.__cached_assets[cached_lookup] = cached_asset

            temp_assets[file_name[0]] = cached_asset

        return temp_assets