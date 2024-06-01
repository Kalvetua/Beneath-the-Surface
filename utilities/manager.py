import pygame


"""
The class 'EntityManager' manages groups of entities. Members of the group gain access to essential, shared functions such as 'update' and 'render'.

"""
class EntityManager:
    def __init__(self):
        self.entities = [] #! List that contains all the entities in the manager.

    #! Function 'update' adjusts logic of all entities in manager. Removes an entity from the manager if it is dead.
    def update(self, dt, quadtree, game):
        self.entities = [entity for entity in self.entities if entity.update(dt, quadtree, game)]

    #! Function 'render' draws all the entities in the manager onto 'screen'.
    def render(self, screen, offset=(0,0)):

        screen.fblits(self.current_image_position(offset)) #! Method 'fblits' renders images of all entities onto 'screen'.

        #! Extra renders; not images of the entities.
        player = self.retr_player()
        #pygame.draw.rect(screen, (50, 0, 255,), (player.x - offset[0], player.y - offset[1], player.w, player.h), 1)

        for entity in self.entities:
            if hasattr(entity, 'attack_view'):
                pygame.draw.rect(screen, (255,0,255), (entity.attack_view.x - offset[0], entity.attack_view.y - offset[1], entity.attack_view.w, entity.attack_view.h), 1)
                pygame.draw.rect(screen, (135,0,255), (entity.x - offset[0], entity.y - offset[1], entity.w, entity.h), 1)
                pass

        #pygame.draw.rect(screen, (255,0,255), (player.attack_boundary.x - offset[0], player.attack_boundary.y - offset[1], player.attack_boundary.w, player.attack_boundary.h), 1)
    
    #! Fuction 'current_image_position' returns a tuple that contains the image + image position of all the entities in the manager.
    def current_image_position(self, offset):
        entities = []

        #! Gathers image and image position of all the entities into a list.
        for entity in self.entities:
            position = [entity.x - (entity.image.get_width() - entity.w) / 2, entity.y - (entity.image.get_height() - entity.h) / 2] #! Image position (not calculated for offsets).

            entities.append((entity.image, [position[n] + entity.local_offset[n] - offset[n] for n in range(2)])) #! Entity's image and image position (calculated for offsets) - appended to temp list.

        return tuple(entities)

    #! Appends singular entity to the manager.
    def add(self, entity):
        self.entities.append(entity)

    #! Appends multiple entities to the manager.
    def add_multiple(self, entities):
        self.entities.extend(entities)

    #! Finds the player in the entity list and returns it.
    def retr_player(self):
        return self.entities[0]

    #! Returns all entities.
    def retrieve_entities(self):
        return self.entities

    #! Returns a number of all entities in the manager.
    def len(self):
        return len(self.entities)