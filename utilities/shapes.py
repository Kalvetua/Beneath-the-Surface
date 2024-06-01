"""
Class Rectangle(): An object with (2D) position and size attributes in a quadrilateral shape.
"""
class Rectangle:
    def __init__(self, position, size):
        self.x = position[0]
        self.y = position[1]
        self.w = size[0]
        self.h = size[1]

    """
    Method union(): Updates position and size of self rectangle to also cover other rectangle.
    """
    def union(self, other):
        xMin = min(self.x, other.x)
        yMin = min(self.y, other.y)
        xMax = max(self.x + self.w, other.x + other.w)
        yMax = max(self.y + self.h, other.y + other.h)

        self.x = xMin
        self.y = yMin
        self.w = xMax - xMin
        self.h = yMax - yMin

    def split(self): # Splits rectangle into quarters
        quarter_size = (self.w / 2, self.h / 2)
        return (
            Rectangle((self.x, self.y), quarter_size), # North West
            Rectangle((self.x + self.w / 2, self.y), quarter_size), # North East
            Rectangle((self.x, self.y + self.h / 2), quarter_size), # South West
            Rectangle((self.x + self.w / 2, self.y + self.h / 2), quarter_size) # South East
            )

    """
    Method collide(): Checks collision of self rectangle with other rectangle, and return a boolean value
    """
    def collide(self, other):
        if (self.x + self.w > other.x and self.x < other.x + other.w and
            self.y + self.h > other.y and self.y < other.y + other.h):
            return True
        else:
            return False

    """
    Method collide_all(): Checks collision of self rectangle with a list of other rectangles, and
    returns a list with all the rectangles that collided with self rectangle
    """
    def collide_all(self, arr):
        hits = []
        for n in range(len(arr)):
            other = arr[n]
            if (self.x + self.w > other.x and
                self.x < other.x + other.w and
                self.y + self.h > other.y and
                self.y < other.y + other.h):
                hits.append(n)
        return hits
    
    def get_pos(self):
        return (self.x, self.y)

    def get_size(self):
        return (self.w, self.h)