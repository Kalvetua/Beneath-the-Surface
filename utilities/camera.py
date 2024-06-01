# Local
from utilities.shapes import Rectangle

"""
Class Camera(): Ensures that only objects within the view of the game window are
displayed. This is primarily to make the program more efficient and to improve fps.
"""
class Camera:
    def __init__(self, size):
        self.x, self.y = 0, 0
        self.w = size[0]
        self.h = size[1]
        self.view = []

    def update(self, quadtree, offset):
        self.view = quadtree.hit( Rectangle(offset, (self.w, self.h)) )

    def render(self, screen, offset=(0,0)):
        screen.fblits(((tile.image, (tile.x - offset[0], tile.y- offset[1])) for tile in self.view))