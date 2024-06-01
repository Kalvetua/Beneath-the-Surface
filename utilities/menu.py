# Standard
from queue import Queue
from threading import Thread

# 3rd part
import pygame

# Local
from .asset import Asset
from .button import Button

class Menu:
    def __init__(self, game):
        # State
        self.run_menu = True

        # 'imports' attributes & methods from the Game class
        self.game = game

        self.buttons = []
        self.names = []

        self.SIZE_BUTTON = (512, 144)
        self.SCALE_BUTTON = (game.res_window[0] // 5, game.res_window[1] // 10)

        self.BUTTON_ASSETS = Asset('button', self.SIZE_BUTTON, self.SCALE_BUTTON)
        
        self.navigation_configs = {
            'Mouse Position' : pygame.mouse.get_pos(),
            'Mouse Mode' : True,
            'Navigation Index' : 0, # Selected button in menu (Non-Mouse Mode)
            'Backward' : False, # Backward buttons active
            'Forward' : False, # Forward buttons active
            'Cooldown' : True, # Ensures a function executes once per key press
        }

        self.mouse_position = pygame.mouse.get_pos()
        self.cooldown = True # Ensures a function executes once per key press
        self.mouse_mode = True
        self.back_pressed = False
        self.forw_pressed = False
        self.button_index = 0

    def navigate_buttons(self):
        key = pygame.key.get_pressed()
        if (key[pygame.K_LEFT] or key[pygame.K_UP]) and not self.back_pressed:

            self.button_index = self.button_index - 1 if self.button_index > 0 else len(self.buttons) - 1

            self.back_pressed = True

            if self.mouse_mode:
                self.mouse_mode = False
                self.button_index = 0

        if not key[pygame.K_LEFT] and not key[pygame.K_UP]:
            self.back_pressed = False

        if (key[pygame.K_RIGHT] or key[pygame.K_DOWN]) and not self.forw_pressed:

            self.button_index = self.button_index + 1 if self.button_index < len(self.buttons) - 1 else 0

            self.forw_pressed = True
            if self.mouse_mode:
                self.mouse_mode = False
                self.button_index = 0

        if not key[pygame.K_RIGHT] and not key[pygame.K_DOWN]:
            self.forw_pressed = False

    def display_reset(self):
        self.button_index = 0
        self.cooldown = True

    def create_buttons(self):
        buttons = []

        index = 0
        for name in self.names:
            temp_asset = self.BUTTON_ASSETS.spritesheets

            funct = {
                'ID' : name,
                'Static' : temp_asset[name + '_static'],
                'Animated' : temp_asset[name + '_spritesheet']
            }

            x = self.game.res_window[0] // 2 - self.SCALE_BUTTON[0] // 2
            y = self.game.res_window[1] // self.divide - self.SCALE_BUTTON[1] + (self.SCALE_BUTTON[1] + self.SCALE_BUTTON[1] // 20) * index

            buttons.append(Button((x, y), self.SCALE_BUTTON, funct))
            index += 1

        return buttons

class MainMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)

        self.names = ['start', 'saves', 'options', 'exit']
        self.divide = 2
        self.buttons = self.create_buttons()

    def input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run_menu = False
                self.game.run_application = False
                self.game.run_level_sequence = False

        mouse, key = pygame.mouse.get_pressed(), pygame.key.get_pressed()
        if not mouse[0] and self.mouse_mode:
            self.cooldown = False
        elif not key[pygame.K_RETURN] and not self.mouse_mode:
            self.cooldown = False

    def update(self):
        self.game.clock.tick(self.game.FRAMES_PER_SECOND)

        self.input()

        self.navigate_buttons()

        for button in self.buttons:
            button.update(self, self.game)

    def render(self):
        self.game.window.fill((11,11,11))

        for button in self.buttons:
            button.render(self.game.window, (0,0))

        mouse_pos = pygame.mouse.get_pos()
        scale = [self.game.res_window[n] / self.game.res_screen[n] for n in range(2)]
        pygame.draw.rect(self.game.window, (255,255,255), (*mouse_pos, 2 * scale[0], 2 * scale[1]))

        pygame.display.update()

    def menu_sequence(self):
        self.button_numb = 0
        self.run_menu = True
        self.cooldown = True

        while self.run_menu:
            self.update()
            self.render()

class LoadMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.progress = 0
        self.queue = Queue()

        self.w = self.game.res_window[0]
        self.h = self.game.res_window[1]

        self.bar_height = 30
        self.bar_width = self.w - self.w / 4

        self.x = self.w / 2 - self.bar_width / 2
        self.y = self.h / 2

        self.fill = 0

    def menu_sequence(self):
        self.run_menu = True
        self.progress = 0
        self.fill = 0
        self.queue = Queue()

        # Starts up a background (sub-) process that loads the assets
        load = Thread(target=self.game.LEVEL_INFO.load_level, args=(self.queue, self.game))
        load.start()

        # The main process that keeps track of input and updates (alt. draws) changes onto screen
        while self.run_menu:
            self.update(load)
            self.render()

    def input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run_menu = False
                self.game.run_application = False
                self.game.run_level_sequence = False

    def update(self, load):
        # Ends when it reaches final level
        if self.game.LEVEL_INFO.current_level >= self.game.LEVEL_INFO.MAX_LEVEL:
            self.run_menu = False
            self.game.run_application = False
            self.game.run_level_sequence = False

        # Limits the framerate (60fps)
        self.game.clock.tick(self.game.FRAMES_PER_SECOND)

        # Overlooks input from mouse and keys
        self.input()

        #
        if not self.queue.empty():
            self.progress = self.queue.get()

        # Increases progress in conjunction with assets loaded
        load_progress = self.progress / 100
        if load_progress >= 1:
            load_progress = 1
            if not load.is_alive():
                self.run_menu = False
                
        self.fill = load_progress * self.bar_width

    def render(self):
        # Resets the background
        self.game.window.fill((11,11,11))

        # Calculates the progress bar dimensions
        outline_rect = (self.x - 10, self.y - 10, self.bar_width + 20, self.bar_height + 20)
        fill_rect = (self.x, self.y, self.fill, self.bar_height)

        # Paints the progress bar onto screen
        pygame.draw.rect(self.game.window, (255,255,255), outline_rect, 2)
        pygame.draw.rect(self.game.window, (255,255,255), fill_rect)

        # Displays changes to the screen
        pygame.display.update()

class PauseMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)

        self.names = ['resume', 'saves', 'options', 'exit']
        self.divide = 2.5
        self.buttons = self.create_buttons()

        self.background = pygame.Surface(self.game.res_window)

    def menu_sequence(self):
        self.button_numb = 0
        self.run_menu = True
        self.cooldown = True

        self.background.blit(self.game.window, (0,0))

        while self.run_menu:
            self.update()
            self.render()

    def update(self):
        self.game.clock.tick(self.game.FRAMES_PER_SECOND)
        
        self.input()

        self.navigate_buttons()
        for button in self.buttons:
            button.update(self, self.game)

    def input(self):
        mouse = pygame.mouse.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.run_menu = False
                self.game.run_application = False

        if not mouse[0]:
            self.cooldown = False

    def render(self):

        self.game.window.blit(self.background, (0,0))

        for button in self.buttons:
            button.render(self.game.window, (0, 0))

        mouse_pos = pygame.mouse.get_pos()
        scale = [self.game.res_window[n] / self.game.res_screen[n] for n in range(2)]
        pygame.draw.rect(self.game.window, (255,255,255), (*mouse_pos, 2 * scale[0], 2 * scale[1]))

        pygame.display.update()
