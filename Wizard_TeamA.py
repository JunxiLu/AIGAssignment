import pygame

from random import randint, random
from Graph import *

from Character import *
from State import *

class Wizard_TeamA(Character):

    def __init__(self, world, image, projectile_image, base, position, explosion_image = None):

        Character.__init__(self, world, "wizard", image)

        self.projectile_image = projectile_image
        self.explosion_image = explosion_image

        self.base = base
        self.position = position
        self.move_target = GameEntity(world, "wizard_move_target", None)
        self.target = None

        self.maxSpeed = 50
        self.min_target_distance = 100
        self.projectile_range = 100
        self.projectile_speed = 100

        seeking_state = WizardStateSeeking_TeamA(self)
        attacking_state = WizardStateAttacking_TeamA(self)
        fleeing_state = WizardStateFleeing_TeamA(self)
        ko_state = WizardStateKO_TeamA(self)

        self.brain.add_state(seeking_state)
        self.brain.add_state(attacking_state)
        self.brain.add_state(fleeing_state)
        self.brain.add_state(ko_state)

        self.brain.set_state("seeking")

    def render(self, surface):

        Character.render(self, surface)


    def process(self, time_passed):
        
        Character.process(self, time_passed)
        
        level_up_stats = ["ranged cooldown", "ranged damage", "speed"]
        if self.can_level_up():
            if self.ranged_cooldown >= 1.5:
                choice = 0
            elif self.maxSpeed < 75:
                choice = 2
            else:
                choice = randint(0, len(level_up_stats) - 1)
            self.level_up(level_up_stats[choice])

    def get_furthest_node(self, position):

        furthest = None
        for node in self.path_graph.nodes.values():
            if furthest is None:
                furthest = node
                furthest_distance = (position - Vector2(furthest.position)).length()
            else:
                distance = (position - Vector2(node.position)).length()
                if distance > furthest_distance:
                    furthest = node
                    furthest_distance = distance

        return furthest

    # def get_nearest_obstacle(self):

    #     for entity in self.world.entities.values():

    #         # neutral entity
    #         if entity.name == "obstacle":
    #             collision_list = pygame.sprite.spritecollide(entity, self.world.obstacles, False, pygame.sprite.collide_mask)
    #             for collide_e in collision_list:
    #                 if collide_e.name == "obstacle":
    #                     self.velocity = 

    def get_enemy_base(self, id):

        enemy_base = None

        for entity in self.world.entities.values():

            if 1 - entity.team_id == id:
                 enemy_base = entity
                 break
        
        return enemy_base


class WizardStateSeeking_TeamA(State):

    def __init__(self, wizard):

        State.__init__(self, "seeking")
        self.wizard = wizard

        self.wizard.path_graph = self.wizard.world.paths[randint(0, len(self.wizard.world.paths)-1)]
        

    def do_actions(self):

        self.wizard.velocity = self.wizard.move_target.position - self.wizard.position
        if self.wizard.velocity.length() > 0:
            self.wizard.velocity.normalize_ip();
            self.wizard.velocity *= self.wizard.maxSpeed

        # check if opponent is in range
        nearest_opponent = self.wizard.world.get_nearest_opponent(self.wizard)
        if nearest_opponent is not None:
            opponent_distance = (self.wizard.position - nearest_opponent.position).length()
            if opponent_distance <= self.wizard.min_target_distance:
                if self.wizard.current_ranged_cooldown <= 0:
                    self.wizard.target = nearest_opponent
                    self.wizard.ranged_attack(self.wizard.target.position, self.wizard.explosion_image)

    def check_conditions(self):

        if (self.wizard.position - self.wizard.move_target.position).length() < 8:

            # continue on path
            if self.current_connection < self.path_length:
                self.wizard.move_target.position = self.path[self.current_connection].toNode.position
                self.current_connection += 1

        # check if opponent is in range
        nearest_opponent = self.wizard.world.get_nearest_opponent(self.wizard)

        if nearest_opponent is not None:
            opponent_distance = (self.wizard.position - nearest_opponent.position).length()
            if nearest_opponent.name == "orc" and opponent_distance <= 50:
                self.wizard.target = nearest_opponent
                return "fleeing"
            if (nearest_opponent.name == "tower" or nearest_opponent.name == "base") and opponent_distance <= self.wizard.min_target_distance:
                self.wizard.target = nearest_opponent
                return "attacking"
            
        return None

    def entry_actions(self):

        nearest_node = self.wizard.path_graph.get_nearest_node(self.wizard.position)

        self.path = pathFindAStar(self.wizard.path_graph, \
                                  nearest_node, \
                                  self.wizard.path_graph.nodes[self.wizard.base.target_node_index])

        
        self.path_length = len(self.path)

        if (self.path_length > 1):
            self.current_connection = 0
            self.wizard.move_target.position = self.path[1].fromNode.position
        elif (self.path_length > 0):
            self.current_connection = 0
            self.wizard.move_target.position = self.path[0].fromNode.position

        else:
            self.wizard.move_target.position = self.wizard.path_graph.nodes[self.wizard.base.spawn_node_index].position

class WizardStateAttacking_TeamA(State):

    def __init__(self, wizard):

        State.__init__(self, "attacking")
        self.wizard = wizard

    def do_actions(self):

        opponent_distance = (self.wizard.position - self.wizard.target.position).length()

        # opponent within range
        if opponent_distance <= self.wizard.min_target_distance:
            if randint(1, 20) == 1:
                rand_pos_x = [(self.wizard.position.x - randint(15, 20)), (self.wizard.position.x + randint(15, 20))]
                rand_pos_y = [(self.wizard.position.y - randint(15, 20)), (self.wizard.position.y + randint(15, 20))]
                self.wizard.velocity = Vector2(rand_pos_x[randint(0, 1)], rand_pos_y[randint(0, 1)]) - self.wizard.position
            
            if self.wizard.velocity.length() > 0:
                self.wizard.velocity.normalize_ip();
                self.wizard.velocity *= self.wizard.maxSpeed

            enemy_base = self.wizard.get_enemy_base(self.wizard.team_id)
            nearest_node = self.wizard.path_graph.get_nearest_node(enemy_base.position)
            if (nearest_node.position - self.wizard.position).length() < self.wizard.min_target_distance*0.5:
                self.wizard.velocity = Vector2(0, 0)

            if self.wizard.current_ranged_cooldown <= 0:
                self.wizard.ranged_attack(nearest_node.position, self.wizard.explosion_image)

    def check_conditions(self):

        opponent_distance = (self.wizard.position - self.wizard.target.position).length()

        # target is gone
        if self.wizard.world.get(self.wizard.target.id) is None or self.wizard.target.ko:
            return "seeking"

        if opponent_distance > self.wizard.min_target_distance:
            return "seeking"

        # if (self.wizard.move_target.position - self.wizard.position).length() < 8:
        #     self.wizard.velocity = Vector2(0, 0)
        #     return "seeking"

        nearest_opponent = self.wizard.world.get_nearest_opponent(self.wizard)
        if nearest_opponent is not None:
            opponent_distance = (self.wizard.position - nearest_opponent.position).length()
            if nearest_opponent.name == "orc" and opponent_distance <= 50:
                return "fleeing"
            
        return None

    def entry_actions(self):

        return None

class WizardStateFleeing_TeamA(State):

    def __init__(self, wizard):

        State.__init__(self, "fleeing")
        self.wizard = wizard

        self.wizard.path_graph = self.wizard.world.paths[randint(0, len(self.wizard.world.paths)-1)]
        

    def do_actions(self):

        if randint(1, 20) == 1:
            rand_pos_x = [(self.wizard.move_target.position[0] - randint(20, 30)), (self.wizard.move_target.position[0] + randint(20, 30))]
            rand_pos_y = [(self.wizard.move_target.position[1] - randint(20, 30)), (self.wizard.move_target.position[1] + randint(20, 30))]
            self.wizard.velocity = Vector2(rand_pos_x[randint(0, 1)], rand_pos_y[randint(0, 1)]) - self.wizard.position
        #self.wizard.velocity = self.wizard.move_target.position - self.wizard.position
        if self.wizard.velocity.length() > 0:
            self.wizard.velocity.normalize_ip();
            self.wizard.velocity *= self.wizard.maxSpeed 

        if self.wizard.current_ranged_cooldown <= 0:
            self.wizard.ranged_attack(self.wizard.target.position, self.wizard.explosion_image)

    def check_conditions(self):

        # target is gone
        if self.wizard.world.get(self.wizard.target.id) is None or self.wizard.target.ko:
            self.wizard.target = None
            return "seeking"

        opponent_distance = (self.wizard.position - self.wizard.target.position).length()
        if opponent_distance > self.wizard.min_target_distance:
            self.wizard.target = None
            return "seeking"

        if (self.wizard.position - self.wizard.move_target.position).length() < 8:

            # continue on path
            if self.current_connection < self.path_length:
                self.wizard.move_target.position = self.path[self.current_connection].toNode.position
                self.current_connection += 1
            
        return None

    def entry_actions(self):

        nearest_node = self.wizard.path_graph.get_nearest_node(self.wizard.position)
        furthest_node = self.wizard.get_furthest_node(self.wizard.position)

        self.path = pathFindAStar(self.wizard.path_graph, \
                                  nearest_node, \
                                  furthest_node)

        
        self.path_length = len(self.path)

        if (self.path_length > 1):
            self.current_connection = 0
            self.wizard.move_target.position = self.path[1].fromNode.position
        elif (self.path_length > 0):
            self.current_connection = 0
            self.wizard.move_target.position = self.path[0].fromNode.position
        else:
            self.wizard.move_target.position = furthest_node

class WizardStateKO_TeamA(State):

    def __init__(self, wizard):

        State.__init__(self, "ko")
        self.wizard = wizard

    def do_actions(self):

        return None


    def check_conditions(self):

        # respawned
        if self.wizard.current_respawn_time <= 0:
            self.wizard.current_respawn_time = self.wizard.respawn_time
            self.wizard.ko = False
            self.wizard.path_graph = self.wizard.world.paths[randint(0, len(self.wizard.world.paths)-1)]
            return "seeking"
            
        return None

    def entry_actions(self):

        self.wizard.current_hp = self.wizard.max_hp
        self.wizard.position = Vector2(self.wizard.base.spawn_position)
        self.wizard.velocity = Vector2(0, 0)
        self.wizard.target = None

        return None
