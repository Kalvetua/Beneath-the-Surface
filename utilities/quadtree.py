# Standard
from copy import copy

from utilities.shapes import Rectangle

""""
Class Quadtree(): Creates a quadtree for a list of objects (with coordinates) that will enable a more
efficient object look-up. A quadtree makes it possible to look for objects only within a certain area
(coordinate plane) instead of iterating though all of the objects in the entire map, as one would do with list.

Resources:
https://stackoverflow.com/questions/41946007/efficient-and-well-explained-implementation-of-a-quadtree-for-2d-collision-det
https://www.cs.cmu.edu/afs/cs/user/glmiller/public/computational-geometry/15-852-F12/Handouts/Har-Peled-Chap2.pdf
"""


class QuadTree(object):
    def __init__(self, items, depth=8, boundary=None):
        # These variables represent the four corners of a leaf / area. Respectively: North West, North East, South East, South West.
        self.nw = self.ne = self.se = self.sw = None

        depth -= 1
        if depth == 0 or not items:
            self.items = items
            return

        # Creates a leaf / area (coordinate plane) large enough to span all the items (data points) in the quarters.
        if boundary:
            boundary = Rectangle( *boundary )
        else:
            boundary = copy(items[0])
            for item in items[1:]:
                boundary.union( item )

        # Center coordinates
        cx = self.cx = ( (boundary.x + boundary.w) / 2 )
        cy = self.cy = ( (boundary.y + boundary.h) / 2 )

        self.items = []
        nw_items = []
        ne_items = []
        se_items = []
        sw_items = []

        for item in items:
            in_nw = item.x <= cx and item.y <= cy
            in_sw = item.x <= cx and item.y + item.h >= cy
            in_ne = item.x + item.h >= cx and item.y <= cy
            in_se = item.x + item.h >= cx and item.y + item.h >= cy

            if in_nw and in_ne and in_se and in_sw:
                self.items.append(item)
            else:
                if in_nw: nw_items.append(item)
                if in_ne: ne_items.append(item)
                if in_se: se_items.append(item)
                if in_sw: sw_items.append(item)

        if nw_items:
            self.nw = QuadTree(nw_items, depth, ( (boundary.x, boundary.y), (cx, cy) ))
        if ne_items:
            self.ne = QuadTree(ne_items, depth, ( (cx, boundary.y), (boundary.x + boundary.w, cy) ))
        if se_items:
            self.se = QuadTree(se_items, depth, ( (cx, cy), (boundary.x + boundary.w, boundary.y + boundary.h) ))
        if sw_items:
            self.sw = QuadTree(sw_items, depth, ( (boundary.x, cy), (cx, boundary.y + boundary.h) ))

    def hit(self, rect):
        hits = set( [ self.items[n] for n in rect.collide_all( self.items ) ] )
                
        if self.nw and rect.x <= self.cx and rect.y <= self.cy:
            hits |= self.nw.hit(rect)
        if self.sw and rect.x <= self.cx and rect.y + rect.h >= self.cy:
            hits |= self.sw.hit(rect)
        if self.ne and rect.x + rect.w >= self.cx and rect.y <= self.cy:
            hits |= self.ne.hit(rect)
        if self.se and rect.x + rect.w >= self.cx and rect.y + rect.h >= self.cy:
            hits |= self.se.hit(rect)

        return hits