import pygame

class Spritesheet:
    def __init__(self, spritesheet, frame_size):
        self.spritesheet = spritesheet
        self.frame_size = frame_size

    def divide_spritesheet(self, colour):
        divided_spritesheet = []
        regular, flipped = [], []

        for frame_number in range(self.spritesheet.get_width() // self.frame_size[0]):
            image = pygame.Surface(self.frame_size).convert_alpha()
            image.fill(colour)
            image.blit(self.spritesheet, (0,0), ((frame_number * self.frame_size[0]), 0, *self.frame_size))
            image.set_colorkey(colour)

            regular.append(image) 
            flipped.append(pygame.transform.flip(image, True, False))

        divided_spritesheet.append(regular)
        divided_spritesheet.append(flipped)

        return divided_spritesheet