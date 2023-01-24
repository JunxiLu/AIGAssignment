import pygame

from random import randint, random
from Graph import *

from Character import *
from State import *

from Functions_Anything import *

class Wizard_Anything(Character):

    def __init__(self, world, image, projectile_image, base, position, explosion_image = None):

        Character.__init__(self, world, "wizard", image)

        self.graph = Graph(self)
        generate_pathfinding_graphs(self, "pathfinding_graph_Anything.txt")

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

        seeking_state = WizardStateSeeking_Anything(self)
        attacking_state = WizardStateAttacking_Anything(self)
        fleeing_state = WizardStateFleeing_Anything(self)
        ko_state = WizardStateKO_Anything(self)

        self.brain.add_state(seeking_state)
        self.brain.add_state(attacking_state)
        self.brain.add_state(fleeing_state)
        self.brain.add_state(ko_state)

        self.brain.set_state("seeking")

    def render(self, surface):

        Character.render(self, surface)


    def process(self, time_passed):
        
        Character.process(self, time_passed)
        
        level_up_stats = ["ranged cooldown", "ranged damage", "speed", "projectile range"]
        if self.can_level_up():
            if self.ranged_cooldown >= 1.5:
                choice = 0
            elif self.maxSpeed < 65:
                choice = 2
            elif self.projectile_range < 240:
                choice = 3
            else:
                choice = 0
            self.level_up(level_up_stats[choice])

    def get_enemy_structure(self, team_id):

        enemy_structures = {}

        for entity in self.world.entities.values():

            if 1 - entity.team_id == team_id and (entity.name == "tower" or entity.name == "base"):
                enemy_structures[entity.id] = entity
        
        return enemy_structures

class WizardStateSeeking_Anything(State):

    def __init__(self, wizard):

        State.__init__(self, "seeking")
        self.wizard = wizard

        self.wizard.path_graph = self.wizard.paths[randint(0, len(self.wizard.paths)-1)]
        

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
            if opponent_distance <= 60:
                if nearest_opponent.name == "orc" or (nearest_opponent.name == "knight" and nearest_opponent.target == self.wizard):
                    self.wizard.target = nearest_opponent
                    return "fleeing"
        
        enemy_structures = self.wizard.get_enemy_structure(self.wizard.team_id)
        for structure in enemy_structures.values():
            # if (self.wizard.position - structure.position).length() <= self.wizard.min_target_distance:
                
            #     self.wizard.target = structure
            #     if self.wizard.team_id == 0:
            #         self.wizard.velocity = Vector2(self.wizard.maxSpeed, self.wizard.maxSpeed)
            #     else:
            #         self.wizard.velocity = Vector2(-self.wizard.maxSpeed, -self.wizard.maxSpeed)
            #     return "attacking"
            if structure.name == "base" and (self.wizard.position - self.wizard.path_graph.nodes[self.wizard.base.target_node_index].position).length() <= self.wizard.min_target_distance:
                
                self.wizard.target = structure
                if self.wizard.team_id == 0:
                    self.wizard.velocity = Vector2(self.wizard.maxSpeed, self.wizard.maxSpeed)
                else:
                    self.wizard.velocity = Vector2(-self.wizard.maxSpeed, -self.wizard.maxSpeed)
                return "attacking"
            
        return None

    def entry_actions(self):

        nearest_node = self.wizard.path_graph.get_nearest_node(self.wizard.position)

        self.path = pathFindAStar(self.wizard.path_graph, \
                                  nearest_node, \
                                  self.wizard.path_graph.nodes[self.wizard.base.target_node_index])

        self.path_length = len(self.path)

        if (collide_obstacle(self.wizard)):
            self.current_connection = 0
            self.wizard.move_target.position = nearest_node.position
        if (self.path_length > 1):
            self.current_connection = 0
            self.wizard.move_target.position = self.path[1].fromNode.position
        elif (self.path_length > 0):
            self.current_connection = 0
            self.wizard.move_target.position = self.path[0].fromNode.position
        else:
            self.wizard.move_target.position = self.wizard.path_graph.nodes[self.wizard.base.target_node_index].position

class WizardStateAttacking_Anything(State):

    def __init__(self, wizard):

        State.__init__(self, "attacking")
        self.wizard = wizard

    def do_actions(self):

        is_targeting = False
        enemy_structures = self.wizard.get_enemy_structure(self.wizard.team_id)
        for structure in enemy_structures.values():
            if structure.target == self.wizard:
                is_targeting = True
                break

        if randint(1, 9) == 1 or is_targeting:
            # rand_pos_x = [(self.wizard.position.x - randint(40, 60)), (self.wizard.position.x + randint(40, 60))]
            # rand_pos_y = [(self.wizard.position.y - randint(40, 60)), (self.wizard.position.y + randint(40, 60))]
            # self.wizard.velocity = Vector2(rand_pos_x[randint(0, 1)], rand_pos_y[randint(0, 1)]) - self.wizard.position
            rand_vec = [Vector2(randint(60,80), randint(-90,-70)), Vector2(randint(-80,-60), randint(70,90))]
            self.wizard.velocity = rand_vec[randint(0,1)]
        
        if self.wizard.velocity.length() > 0:
            self.wizard.velocity.normalize_ip();
            self.wizard.velocity *= self.wizard.maxSpeed

        if self.wizard.current_ranged_cooldown <= 0:
            self.wizard.ranged_attack(self.wizard.world.graph.nodes[self.wizard.base.target_node_index].position, self.wizard.explosion_image)

    def check_conditions(self):

        opponent_distance = (self.wizard.position - self.wizard.target.position).length()
        base_distance = (self.wizard.world.graph.nodes[self.wizard.base.target_node_index].position - self.wizard.position).length()

        if base_distance > self.wizard.min_target_distance*2-30:
            return "seeking"
        elif base_distance <= self.wizard.min_target_distance/2+40:
            if self.wizard.team_id == 0:
                self.wizard.velocity = Vector2(-self.wizard.maxSpeed, -self.wizard.maxSpeed)
            else:
                self.wizard.velocity = Vector2(self.wizard.maxSpeed, self.wizard.maxSpeed)
            return "attacking"

        nearest_opponent = self.wizard.world.get_nearest_opponent(self.wizard)
        if nearest_opponent is not None:
            opponent_distance = (self.wizard.position - nearest_opponent.position).length()
            if opponent_distance <= self.wizard.min_target_distance:
                if opponent_distance <= 60:
                    if nearest_opponent.name == "orc" or nearest_opponent.name == "knight":
                        self.wizard.target = nearest_opponent
                        return "fleeing"
                    elif (nearest_opponent.name == "archer" or nearest_opponent.name == "wizard") and nearest_opponent.target == self.wizard:
                         self.wizard.target = nearest_opponent
                         return "fleeing"                       
                else:
                    if (nearest_opponent.name == "archer" or nearest_opponent.name == "wizard") and nearest_opponent.target == self.wizard:
                        self.wizard.target = nearest_opponent
                        return "fleeing"
            
        return None

    def entry_actions(self):

        return None

class WizardStateFleeing_Anything(State):

    def __init__(self, wizard):

        State.__init__(self, "fleeing")
        self.wizard = wizard

        self.wizard.path_graph = self.wizard.paths[randint(0, len(self.wizard.paths)-1)]
        

    def do_actions(self):

        if self.wizard.target.name == "wizard" or self.wizard.target.name == "archer":
            if randint(1, 9) == 1:
                rand_pos_x = [(self.wizard.position.x - randint(40, 60)), (self.wizard.position.x + randint(40, 60))]
                rand_pos_y = [(self.wizard.position.y - randint(40, 60)), (self.wizard.position.y + randint(40, 60))]
                self.wizard.velocity = Vector2(rand_pos_x[randint(0, 1)], rand_pos_y[randint(0, 1)]) - self.wizard.position
        else:
            self.wizard.velocity = self.wizard.move_target.position - self.wizard.position

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
            else:
                return "fleeing"
            
        return None

    def entry_actions(self):

        nearest_node = self.wizard.path_graph.get_nearest_node(self.wizard.position)
        furthest_node = get_furthest_node(self.wizard, self.wizard.position)

        if nearest_node == self.wizard.path_graph.nodes[self.wizard.base.spawn_node_index]:
            self.path = pathFindAStar(self.wizard.graph, \
                                    nearest_node, \
                                    furthest_node)
        else:
            self.path = pathFindAStar(self.wizard.path_graph, \
                                    nearest_node, \
                                    self.wizard.path_graph.nodes[self.wizard.base.spawn_node_index])

        
        self.path_length = len(self.path)

        if (self.path_length > 1):
            self.current_connection = 0
            self.wizard.move_target.position = self.path[1].fromNode.position
        if (self.path_length > 0):
            self.current_connection = 0
            self.wizard.move_target.position = self.path[0].fromNode.position
        else:
            self.wizard.move_target.position = self.wizard.path_graph.nodes[self.wizard.base.spawn_node_index]

class WizardStateKO_Anything(State):

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
            self.wizard.path_graph = self.wizard.paths[randint(0, len(self.wizard.paths)-1)]
            return "seeking"
            
        return None

    def entry_actions(self):

        self.wizard.current_hp = self.wizard.max_hp
        self.wizard.position = Vector2(self.wizard.base.spawn_position)
        self.wizard.velocity = Vector2(0, 0)
        self.wizard.target = None

        return None
