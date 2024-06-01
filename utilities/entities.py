 # Standard
import random

# 3rd party
import pygame

# Local
from .shapes import Rectangle
from .physics import Physics


class EntityAnimation:
    def __init__(self, image, assets):
        self.image = image
        self.assets = assets

        self.previous_animation = None
        self.current_animation = None

        self.fIndex = 0
        self.tick = 0
        self.framerate = 6

    def update_entity_animation(self, flipped, attack, direction, health):

        if attack != True:
            self.framerate = 6

            # Idle & Horizontal movement
            if self.velocity[0] == 0:
                self.current_animation = self.assets.get('idle', self.current_animation)

            elif self.velocity[0] != 0:
                self.current_animation = self.assets.get('run', self.current_animation)

            # Vertical movement (overides idle and horizontal)
            if self.velocity[1] < 0:
                self.current_animation = self.assets.get('jump', self.current_animation)

            elif self.velocity[1] > 0:
                self.current_animation = self.assets.get('fall', self.current_animation)

            elif self.velocity[1] == 0 and direction['DOWN'] != True:
                self.current_animation = self.assets.get('transition', self.current_animation)

        else:
            self.current_animation = self.assets.get('attack', self.current_animation)

        if health <= 0:
            self.current_animation = self.assets.get('death', self.current_animation)

        if self.current_animation != self.previous_animation:
            self.fIndex = 0

            self.previous_animation = self.current_animation

            if 'attack' in self.assets.keys():
                if self.current_animation == self.assets['attack']:
                    self.framerate = 2

        # Determines the speed of an animation
        if self.tick >= self.framerate:
            self.fIndex += 1
            self.tick = 0
        else:
            self.tick += 1

        # Resets the cycle of animation
        if self.fIndex >= len(self.current_animation[0]):
            if direction['DOWN'] != True:
                self.fIndex = len(self.current_animation[0]) - 1
            else:
                self.fIndex = 0

            if 'attack' in self.assets.keys():
                if self.current_animation == self.assets['attack']:
                    self.attack = False

        # Updates variables based on which direction the player faces
        self.image = self.current_animation[0][self.fIndex] if not flipped else self.current_animation[1][self.fIndex]


"""
Class Player(): Contains attributes and configurations for the player unit, as well as
the update() method to update said configurations, such as position, appearance and gravity
during each game frame.

"""
class Player(Rectangle, Physics, EntityAnimation):
    def __init__(self, image, position, size, assets=None):
        EntityAnimation.__init__(self, image, assets)
        Rectangle.__init__(self, position, size)
        Physics.__init__(self, position)

        self.is_alive = True
        self.health = 100

        self.grace_period = False
        self.grace_duration = 50
        self.grace_timer = 0

        self.local_offset = [0, 13]

        self.dx = 0
        self.dy = 0
        self.flipped = False

        self.moving = False
        self.airborne = False

        self.attack = False
        self.attack_region = Rectangle(position, (52, self.h))

        self.interact = False
        self.prev_keys = None

        self.door = Rectangle((1918, 169), (20, 32))

    def update(self, dt, static, game):

        # mouse and keyboard
        self.input(game)

        #if self.interact:
        #    print('yep')

        if self.health <= 0:
            self.reset_velocity()
            self.dx = 0
            self.dy = 0

        # physics and collision
        for _ in range(10):
            self.update_verlet(dt, (self.dx, self.dy))

        self.check_collision(static)

        # Performs a certain function depending on collision type
        for id in self.tile_id:
            if id in [2,3,4]:
                game.run_level_sequence = False
                if id == 3:
                    game.LEVEL_INFO.current_level -= 1
                elif id == 4:
                    game.LEVEL_INFO.current_level += 1

        # Animation
        self.update_entity_animation(self.flipped, self.attack, self.dir, self.health)

        # Image offset that centers its position to the entity hitbox
        self.local_offset[0] = -7 if self.flipped else 7

        # Updates the hitbox of the player's attack
        if self.current_animation != self.assets['attack'] or self.fIndex <= len(self.assets['attack'][0]) // 4:
            self.attack_region.x = self.x - self.attack_region.w if self.flipped else self.x + self.w

        self.attack_region.y = self.y

        # Stops the character on the x-axis when no horizontal force is applied
        if self.dx == 0: self.previous_position = (self.current_position[0], self.previous_position[1])

        # Reset forces
        self.dx = 0
        self.dy = 0

        # When grace period is active the player is immune to enemy damage,
        # and this tracks time until it deactivates again.
        if self.grace_period == True:
            if self.grace_timer >= self.grace_duration:
                self.grace_period = False
                self.grace_timer = 0
            else:
                self.grace_timer += 1

        # Terminates player if health reaches 0.
        
        if self.health <= 0:
            if 'death' in self.assets.keys():
                if self.fIndex >= len(self.current_animation[0]) - 1:
                    self.is_alive = False
            else:
                self.is_alive = False
            
            self.health = 0

        if self.is_alive != True:
            game.run_level_sequence = False
        
        return self.is_alive

    def input(self, game):
        key = pygame.key.get_pressed() # Keyboard input

        if key[pygame.K_a]:
            self.dx -= 6
            self.flipped = True

        if key[pygame.K_d]:
            self.dx += 6
            self.flipped = False

        if key[pygame.K_w]:
            if not self.airborne:
                self.dy -= 9.81 * 23
                self.airborne = True
        else:
            if self.airborne and self.dir['DOWN']:
                self.airborne = False

        #if key[pygame.K_f]:
        #    if not self.interact:
        #        if self.collide(self.door):
        #            self.interact = True
        #else:
        #    if self.interact:
        #        self.interact = False

        mouse = pygame.mouse.get_pressed() # Mouse input
        mouse_pos = pygame.mouse.get_pos() # Position of the mouse cursor

        if not game.button_cooldown:
            if mouse[0]:
                game.button_cooldown = True

                if self.attack != True:
                    self.attack = True
                    if mouse_pos[0] * 1 / game.res_offset[0] <= self.x - game.offset[0]:
                        self.flipped = True
                    else:
                        self.flipped = False

class Remnant(Rectangle, Physics, EntityAnimation):
    def __init__(self, image, position, size, assets=None):
        EntityAnimation.__init__(self, image, assets)
        Rectangle.__init__(self, position, size)
        Physics.__init__(self, position)

        self.is_alive = True
        self.health = 100

        self.local_offset = [0, -5]
        self.flipped = random.choice([True, False])
        self.attack = False

        self.imminent_death = False

        self.dx = 0
        self.dy = 0

        self.velx = 0

        self.view = Rectangle((self.x + self.w / 2 - (self.w * 10) / 2, self.y), (self.w * 10, self.h))
        self.bullets = []

    def update(self, dt, static, game):
        player = game.LEVEL_INFO.entities.retr_player()

        # Applies force to axes
        self.input()

        # Movement direction
        if self.dx != 0: self.reverse_direction(static)

        # Tracks player attack as well as the collision between this entity and the player
        self.player_collision(player, game)

        """
        for i, bullet in enumerate(self.bullets):
            if bullet.collide(player):
                player.health -= 20
                # maybe create a manager for them instead?
        """

        # Physics (~gravity)
        for _ in range(10):
            self.update_verlet(dt, (self.dx, self.dy))

        # Collision
        self.check_collision(static)

        # Movement direction
        if self.dir['LEFT'] or self.dir['RIGHT']:
            if self.flipped:
                self.flipped = False
            else:
                self.flipped = True

        # Progresses animation to the next frame, and changes animation under certain conditions
        self.update_entity_animation(self.flipped, self.attack, self.dir, self.health)

        # Image offset that centers its position to the entity hitbox
        self.local_offset[0] = -26 if self.flipped else 26

        # Updates the area visible to this entity
        self.view.x = self.x + self.w / 2 - (self.w * 10) / 2
        self.view.y = self.y

        # Death is delayed until the player's attack animation is 1/4 done

        if self.imminent_death == True and player.fIndex >= len(player.assets['attack'][0]) // 4:
            self.is_alive = False

            # Spawns an 'total' amount of particles where this entity dies
            particles = []
            total = 20

            for _ in range(total):
                w = h = random.randint(3, 6)
                image = pygame.Surface((w, h))
                image.fill((185,185,185))
                particles.append(Blood(image, (self.x+self.w/2, self.y+self.h/2), (w, h)))

            game.LEVEL_INFO.entities.add_multiple(particles)

        # Quite self-explanatory - this entity is terminated if it isn't alive
        return self.is_alive

    def input(self):
        self.dx = self.dx - self.velx if not self.flipped else self.dx + self.velx

    def reverse_direction(self, static):
        if self.lookout(static, self.flipped):
            self.flipped = False if self.flipped else True
            
    def player_collision(self, player, game):
        if self.view.collide(player):
            self.flipped = False if player.x >= self.x else True
            self.bullets.append(Bullet((self.x if self.flipped else self.x + self.w, self.y + self.h / 2), (2, 1), self.flipped))

        if player.grace_period == False:
            if self.collide(player):
                if player.health > 0:
                    game.screen_shake = 25
                    game.hurt = 15
                    player.health -= 20
                else:
                    player.health = 0
                player.reset_velocity()
                player.grace_period = True

        if player.attack == True:
            if self.collide(player.attack_region):
                self.imminent_death = True
                self.health -= 20
                

class Bullet(Rectangle):
    def __init__(self, position, size, direction):
        Rectangle.__init__(self, position, size)

        self.vel = 3 if direction else -3

    def update(self):
        self.x += self.x

class Blood(Rectangle, Physics):
    def __init__(self, image, position, size, assets=None):
        Rectangle.__init__(self, position, size)
        Physics.__init__(self, position)

        self.image = image
        self.assets = assets
        self.local_offset = [0, 0]

        self.is_alive = 1

        self.dx = 0
        self.dy = 0

        self.initial_impact = True

        self.time = random.randint(20, 35)
        self.decay = random.randint(36, 64)

    def update(self, dt, static, game):
        # applies force of initial impact
        if self.initial_impact:
            self.dx = (random.randint(0, 42) / 6 - 3.5) / dt
            self.dy = (random.randint(0, 42) / 6 - 3.5) / dt
            self.initial_impact = False

        # physics
        for _ in range(10):
            self.update_verlet(dt, (self.dx, self.dy), False)
        
        # collision
        self.check_collision(static)

        # timepspan decay
        self.time = self.time - dt * 10

        # timeout means death
        if self.time <= 0:
            self.is_alive = False

        # reset force on both axes
        self.dx, self.dy = 0,0
        
        # alive or dead
        return self.is_alive

class Tile(Rectangle):
    def __init__(self, image, position, size, id=None):
        Rectangle.__init__(self, position, size)

        self.image = image
        self.id = id if id else None

    def render(self, screen, offset=(0,0)):
        screen.blit(self.image, (int(self.x - offset[0]), int(self.y - offset[1])))