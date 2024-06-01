# Standard
import random

# 3rd party
import pygame

# Local
from utilities.menu import MainMenu, LoadMenu, PauseMenu
from utilities.load import LevelInfo
from utilities.camera import Camera


"""
Class Game(): Contains variables (alt. attributes) that are vital to the game, such as
the objects for the application window and display screen, resolution settings, fps and
the internal clock, map information (background, foreground, enemies, player, collision,
etc), and more.

The class also contains the functions (alt. methods) that will assist the game loop process- that is not menus,
which means that it will update entities and objects (+ their physics), as well as render all the visuals onto
the screen - such as the background, foreground, enmemies, player, etc.
"""
class Game:
    def __init__(self):
        pygame.init()

        # States
        self.run_application = True
        self.run_level_sequence = False

        # Resolutions
        DEFAULT_SCREEN_RESOLUTION = (400, 225)

        self.res_window = (1920, 1080)
        self.res_screen = DEFAULT_SCREEN_RESOLUTION
        self.res_offset = [self.res_window[n] / self.res_screen[n] for n in range(2)]

        # Displays
        self.window = pygame.display.set_mode(self.res_window)
        self.screen = pygame.Surface(self.res_screen)

        # Title and Icon
        pygame.display.set_caption('Below the Surface')

        icon = pygame.image.load('images/icon/icon.png').convert_alpha()
        pygame.display.set_icon(icon)

        # Current level information
        self.LEVEL_INFO = LevelInfo()

        self.FONT = pygame.font.SysFont('comic sans', 15, True)

        # Time
        self.clock = pygame.time.Clock()
        self.FRAMES_PER_SECOND = 60

        # Camera
        self.camera = Camera(self.res_screen)

        self.offset = [0,0]
        self.target = None

        self.screen_shake = 0

        self.hurt_indicator = pygame.Surface(self.res_screen, pygame.SRCALPHA)
        self.hurt_indicator = self.hurt_indicator.convert_alpha()
        self.hurt_indicator.fill((139,0,0,30))
        self.hurt = 0

        self.death_screen = pygame.Surface(self.res_screen, pygame.SRCALPHA)
        self.death_screen = self.death_screen.convert_alpha()
        self.death_screen.fill((0,0,0,110))

        # Hide mouse cursor
        pygame.mouse.set_visible(False)

        self.button_cooldown = False

        # Menus
        self.MENU = {
            'MAIN' : MainMenu(self),
            'PAUSE' : PauseMenu(self),
            'SAVES' : None,
            'OPTIONS' : None,
            'LOADING' : LoadMenu(self)
        }
        
        self.current_menu = self.MENU['MAIN']

    # A method within which is a loop that runs an instance of a level
    def level_sequence(self):
        self.button_cooldown = True
        while self.run_level_sequence:
            self.update() # Updates physics and the logic of the level
            self.render() # Draws (alt. updates) the visuals on the screen and window
    
    def update(self):
        self.clock.tick(self.FRAMES_PER_SECOND) # Limits the FPS
        dt = 1 / self.FRAMES_PER_SECOND # Time between frames (dt = delta time)

        self.input() # Checks input from mouse and keyboard

        self.LEVEL_INFO.entities.update(dt, self.LEVEL_INFO.static, self) # Updates the physics and logic for dynamic objects (such as the player, enemies, particles, etc)

        self.offset = [self.offset[n] + ([self.target.x + self.target.w / 2, self.target.y + self.target.h / 2][n] - self.res_screen[n] / [2, 1.8][n] - self.offset[n]) // 12 for n in range(2)] # Updates the visual offset-
        # (objects remain at their original coordinates, however, the offset creates the illusion of player movement where objects - even static - move relative to the players position)

        shake_power = 6
        if self.target.health <= 0:
            shake_power = 64

        if self.screen_shake > 0:
            self.screen_shake -= 1
            self.offset = [self.offset[n] + random.randint(0, shake_power) - shake_power / 2 for n in range(2)]

        if self.hurt > 0:
            self.hurt -= 1

        self.camera.update(self.LEVEL_INFO.static, self.offset)

        #pointer_position = [pygame.mouse.get_pos()[n] / self.res_offset[n] + self.offset[n] for n in range(2)]
        #print(f'{pointer_position}')

    def input(self):
        key = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run_level_sequence = False
                self.run_application = False

        if key[pygame.K_ESCAPE]:
            self.run_level_sequence = False
            self.current_menu = self.MENU['PAUSE']

        mouse = pygame.mouse.get_pressed()
        if not mouse[0]:
            self.button_cooldown = False

    def render(self):
        if (screen := self.screen): # is there a screen...? If so, render visuals onto it.

            screen.fill((11,11,11)) # Base background
                
            if (background := self.LEVEL_INFO.background):
                screen.blit(background, (16 - self.offset[0], -self.offset[1] - 1)) # Background

            self.LEVEL_INFO.entities.render(screen, self.offset) # Entities (such as the player and the enemies)

            if (foreground := self.LEVEL_INFO.foreground):
                screen.blit(foreground, (16 - self.offset[0], -self.offset[1] - 1)) # Foreground
            else:
                self.camera.render(screen, self.offset) # displays the collidable blocks # The level boundaries

            #pygame.draw.rect(screen, (255,0,255), (self.target.door.x - self.offset[0], self.target.door.y - self.offset[1], self.target.door.w, self.target.door.h), 1)

            health_colour = [0,0,0]
            health_shake = [0,0]
            if self.target.health > 60:
                health_colour = (255,255,255)
            elif self.target.health > 40:
                health_colour = (155,40,0)
                health_shake = [random.randint(0, 1) - 0.5 for _ in range(2)]
            elif self.target.health > 20:
                health_colour = (139,20,0)
                health_shake = [random.randint(0, 2) - 1 for _ in range(2)]
            elif self.target.health > 0:
                health_colour = (139,0,0)
                health_shake = [random.randint(0, 4) - 2 for _ in range(2)]

            if self.hurt:
                screen.blit(self.hurt_indicator, (0,0))
            #if self.target.health <= 0:
            #    screen.blit(self.death_screen, (0,0))

            player_health = self.FONT.render(f'HP:{self.target.health}', True, health_colour)
            screen.blit(player_health, (5 + health_shake[0], 0 + health_shake[1]))

            if self.run_level_sequence:
                mouse_pos = pygame.mouse.get_pos()
                pygame.draw.rect(screen, (255,255,255), (mouse_pos[0] / self.res_offset[0], mouse_pos[1] / self.res_offset[1], 2, 2)) # Renders a custom mouse cursor

            # Upscales screen resolution to match size of window
            self.window.blit(pygame.transform.scale(screen, self.res_window), (0,0))
            pygame.display.update()