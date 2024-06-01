# Standard
import os

# 3rd party
import pygame

"""
Class Asset(): Searches for images in a given folder, subsequently loads them into memory, and
then assigns those images to a public attribute to be used by other classes and objects.
"""
class Asset:
    cached_spritesheets = {}
    
    """
    Method __init__: Initialises assets / images to a public attribute by calling update_spritehsheet().
    """
    def __init__(self, folder_name, size, scale=None):
        # name options: background, button, icon, player
        self.folder_name = folder_name.lower()
        self.size = size
        self.scale = size if not scale else scale

        self.update_spritesheets()

    """
    Method update_spritesheets(): Checks if the requested images are already stored in memory - otherwise
    it calls find() and stores them into memory - and then it assigns the assets to the public attribute.
    """
    def update_spritesheets(self):
        cached_lookup = self.folder_name

        if not (cached_spritesheet := self.cached_spritesheets.get(cached_lookup, None)):
            cached_spritesheet = self.find()

            self.cached_spritesheets[cached_lookup] = cached_spritesheet

        self.spritesheets = cached_spritesheet[self.folder_name]

    """
    Method find(): Looks through root directory in search of images and loads them. In the case of
    spritesheets, they are cut into individual frames and stored as a list.
    """
    def find(self):
        folders = [(root.replace('\\', '/'), subdir, files) for root, subdir, files in os.walk(os.getcwd())]
        colour = (146, 36, 210)
        assets = {}

        for path, _, files in folders:
            if self.folder_name in path.lower() and files:
                folder_name = path.rpartition('/')[2]
                assets[folder_name] = {}

                for file in files:
                    image = pygame.image.load(path + '/' + file).convert_alpha()

                    frames = []
                    amount = image.get_width() // self.size[0]

                    for i in range(amount):
                        frame = pygame.Surface(self.size).convert_alpha()
                        frame.fill(colour)
                        frame.blit(image, (0, 0), ((i * self.size[0]), 0, *self.size))
                        frame = pygame.transform.scale(frame, self.scale)
                        frame.set_colorkey(colour)

                        frames.append(frame)

                    if len(frames) == 1:
                        assets[folder_name].update({file.rpartition('.')[0] : frames[0]})
                    else:
                        assets[folder_name].update({file.rpartition('.')[0] : frames})

        return assets