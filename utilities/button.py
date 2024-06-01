# 3rd party
import pygame

# Local
from .shapes import Rectangle

class Button(Rectangle):
    def __init__(self, position, size, button_info):
        Rectangle.__init__(self, position, size)

        self.id = button_info['ID']
        self.static = button_info['Static']

        self.image = self.static
        self.frames = button_info['Animated']
        self.frames_index = 0

        self.framerate = 0
        self.framerate_limit = 1

    def update(self, menu, game):
        key = pygame.key.get_pressed()

        if menu.mouse_position != pygame.mouse.get_pos(): # If the current mouse position is different from the previous mouse positon, enable mouse mode.
            menu.mouse_mode = True
            menu.mouse_position = pygame.mouse.get_pos()
            menu.button_index = 0
            
        # Enables button animation when mouse hovers over a button or one of LEFT/RIGHT/UP/DOWN keys are pressed.
        if (self.collide(Rectangle(pygame.mouse.get_pos(), (1, 1))) and menu.mouse_mode) or (self.id == menu.names[menu.button_index] and not menu.mouse_mode):
            self.image = self.frames[self.frames_index]
            
            if self.frames_index < len(self.frames) - 1 and self.framerate % self.framerate_limit == 0:
                self.frames_index += 1
            else:
                self.frames_index = 0

            self.framerate = self.framerate + 1 if self.framerate != self.framerate_limit else 0
            
            # Changes menu if a button is pressed.
            if (pygame.mouse.get_pressed()[0] and menu.mouse_mode and not menu.cooldown) or (key[pygame.K_RETURN] and not menu.mouse_mode and not menu.cooldown):
                if self.id == 'start':
                    game.current_menu = game.MENU['LOADING']
                    game.LEVEL_INFO.current_level = 0

                elif self.id == 'resume':
                    game.run_level_sequence = True
                    game.current_menu = game.MENU['LOADING']

                elif self.id == 'saves':
                    game.current_menu = game.MENU['SAVES']
                    
                elif self.id == 'options':
                    game.current_menu = game.MENU['OPTIONS']

                elif self.id == 'exit':
                    if game.current_menu == game.MENU['PAUSE']:
                        game.current_menu = game.MENU['MAIN']

                    elif game.current_menu == game.MENU['MAIN']:
                        game.run_application = False

                menu.run_menu = False

        else:
            self.frames_index = 0
            self.image = self.static

    def render(self, screen, offset=(0,0)):
        screen.blit(self.image, (self.x - offset[0], self.y - offset[1]))