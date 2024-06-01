from utilities.shapes import Rectangle

class Physics: # Enables gravity through verlet integration and collision detection for it
    def __init__(self, position, mass=1, gravity=(0, 9.81)):
        self.current_position = position
        self.previous_position = position

        self.velocity = [0,0]

        self.dir = {'RIGHT' : False, 'LEFT' : False, 'DOWN' : False, 'UP' : False}
        self.tile_id = set()
        self.illuminate = []

        self.MASS = mass
        self.GRAVITY = gravity
        self.RESISTANCE = (9.81 * 100, 0)
        
    def update_verlet(self, dt, force=(0,0), apply_drag=True):
        # Current velocity
        velocity = [self.current_position[n] - self.previous_position[n] for n in range(2)]

        # Current acceleration
        acceleration = [(force[n] + self.GRAVITY[n]) / self.MASS for n in range(2)]

        # Current resistance (if enabled)
        resistance = [self.RESISTANCE[n] * velocity[n] * dt for n in range(2)] if apply_drag else [0 for _ in range(2)]

        # Updates previous position to the current position
        self.previous_position = [self.current_position[n] for n in range(2)]

        # Updates current position with verlet integration, with the addition of resistance
        self.current_position = [self.current_position[n] + velocity[n] + (acceleration[n] - resistance[n]) * dt**2 for n in range(2)]

    def check_collision(self, quadtree):
        self.dir = {'RIGHT' : False, 'LEFT' : False, 'DOWN' : False, 'UP' : False}
        self.tile_id = set()
        self.illuminate = []

        # Calculates current velocity on the x-axis
        velx = self.current_position[0] - self.previous_position[0]

         # Updates entity to the current position on x-axis
        self.x = self.current_position[0]

        # Checks for collisions on the x-axis and updates position based on result
        collisions = quadtree.hit(self)
        for tile in collisions:
            self.tile_id.add(tile.id)
            if velx > 0: # RIGHT
                self.x = tile.x - self.w
                self.current_position[0] = self.x
                self.previous_position[0] = self.x
                self.dir['RIGHT'] = True

            elif velx < 0: # LEFT
                self.x = tile.x + tile.w
                self.current_position[0] = self.x
                self.previous_position[0] = self.x
                self.dir['LEFT'] = True

        self.illuminate += collisions

        # Calculates current velocity on the y-axis
        vely = self.current_position[1] - self.previous_position[1]

        # Updates entity to the current position on y-axis
        self.y = self.current_position[1]

        # Checks for collisions on the y-axis and updates position based on result
        collisions = quadtree.hit(self)
        for tile in collisions:
            self.tile_id.add(tile.id)
            if vely > 0: # BOTTOM / DOWNWARDS
                self.y = tile.y - self.h
                self.current_position[1] = self.y
                self.previous_position[1] = self.y
                self.dir['DOWN'] = True

            elif vely < 0: # TOP / UPWARDS
                self.y = tile.y + tile.h
                self.current_position[1] = self.y
                self.previous_position[1] = self.y
                self.dir['UP'] = True

        self.illuminate += collisions

        self.velocity = [self.current_position[n] - self.previous_position[n] for n in range(2)]

    def reset_velocity(self):
        self.previous_position = self.current_position

    def lookout(self, quadtree, flipped):
        dx = 1 if flipped else -1

        result = False if quadtree.hit(Rectangle( (int(self.x + dx), int(self.y + 1)), (self.w, self.h) )) else True

        self.previous_position = self.current_position
        return result