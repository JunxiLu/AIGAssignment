import pygame

from random import randint, random
from Graph import *

from Character import *
from State import *

from Functions_Anything import *

class Knight_Anything(Character):

    def __init__(self, world, image, base, position):

        Character.__init__(self, world, "knight", image)

        self.graph = Graph(self)
        generate_pathfinding_graphs(self, "pathfinding_graph_Anything.txt")

        self.base = base
        self.position = position
        self.move_target = GameEntity(world, "knight_move_target", None)
        self.target = None

        self.maxSpeed = 80
        self.min_target_distance = 100
        self.melee_damage = 20
        self.melee_cooldown = 2.

        seeking_state = KnightStateSeeking_Anything(self)
        attacking_state = KnightStateAttacking_Anything(self)
        fleeing_state = KnightStateFleeing_Anything(self)
        ko_state = KnightStateKO_Anything(self)

        self.brain.add_state(seeking_state)
        self.brain.add_state(attacking_state)
        self.brain.add_state(fleeing_state)
        self.brain.add_state(ko_state)

        self.brain.set_state("seeking")
        

    def render(self, surface):

        Character.render(self, surface)


    def process(self, time_passed):
        
        Character.process(self, time_passed)

        level_up_stats = ["hp", "speed", "melee damage", "melee cooldown", "healing", "healing cooldown"]
        if self.can_level_up():
            if self.healing_cooldown <= 1.5 :
                choice = 0
                self.level_up(level_up_stats[choice])
            else:
                choice = 5
                self.level_up(level_up_stats[choice])

    def find_wizard(self, knight):
        ally_wizard = None
        self.knight = knight
        for entity in self.knight.world.entities.values():
            if entity.name == 'wizard' and entity.team_id == self.knight.team_id:
                ally_wizard = entity
        return ally_wizard
   


class KnightStateSeeking_Anything(State):

    def __init__(self, knight):

        State.__init__(self, "seeking")
        self.knight = knight

        self.knight.path_graph = self.knight.paths[randint(0, len(self.knight.paths)-1)]


    def do_actions(self):

        self.knight.velocity = self.knight.move_target.position - self.knight.position
        
        if self.knight.velocity.length() > 0:
            self.knight.velocity.normalize_ip();
            self.knight.velocity *= self.knight.maxSpeed
        if self.knight.current_hp <= self.knight.max_hp:
            self.knight.heal();


    def check_conditions(self):

        ally_wizard = self.knight.find_wizard(self.knight)
        if self.knight.path_graph != ally_wizard.path_graph:    
            self.knight.path_graph = ally_wizard.path_graph
            
            return "seeking"
        # check if opponent is in range
        nearest_opponent = self.knight.world.get_nearest_opponent(self.knight)
        if nearest_opponent is not None:
            opponent_distance = (self.knight.position - nearest_opponent.position).length()
            if opponent_distance <= self.knight.min_target_distance:
                    self.knight.target = nearest_opponent
                    return "attacking"
        
        if (self.knight.position - self.knight.move_target.position).length() < 8:

            # continue on path
            if self.current_connection < self.path_length:
                self.knight.move_target.position = self.path[self.current_connection].toNode.position
                self.current_connection += 1
       
        return None
        


    def entry_actions(self):

        
        nearest_node = self.knight.path_graph.get_nearest_node(self.knight.position)

        self.path = pathFindAStar(self.knight.path_graph, \
                                  nearest_node, \
                                  self.knight.path_graph.nodes[self.knight.base.target_node_index])

        
        self.path_length = len(self.path)

        if (collide_obstacle(self.knight)):
            self.current_connection = 0
            self.knight.move_target.position = nearest_node.position
        elif (self.path_length > 1):
            self.current_connection = 0
            self.knight.move_target.position = self.path[1].fromNode.position
        elif (self.path_length > 0):
            self.current_connection = 0
            self.knight.move_target.position = self.path[0].fromNode.position

        else:
            self.knight.move_target.position = self.knight.path_graph.nodes[self.knight.base.target_node_index].position


class KnightStateAttacking_Anything(State):

    def __init__(self, knight):

        State.__init__(self, "attacking")
        self.knight = knight

    def do_actions(self):

        # colliding with target
        if pygame.sprite.collide_rect(self.knight, self.knight.target):
            self.knight.velocity = Vector2(0, 0)
            self.knight.melee_attack(self.knight.target)

        else:
            self.knight.velocity = self.knight.target.position - self.knight.position
            if self.knight.velocity.length() > 0:
                self.knight.velocity.normalize_ip();
                self.knight.velocity *= self.knight.maxSpeed


    def check_conditions(self):

        # target is gone
        if self.knight.world.get(self.knight.target.id) is None or self.knight.target.ko:
            self.knight.target = None
            return "seeking"
        
        
        if  self.knight.current_hp <= self.knight.max_hp * 3/10 :
            
            return "fleeing"
            
        return None

    def entry_actions(self):

        return None

class KnightStateFleeing_Anything(State):

    def __init__(self, knight):

        State.__init__(self, "fleeing")
        self.knight = knight

        self.knight.path_graph = self.knight.paths[randint(0, len(self.knight.paths)-1)]
        

    def do_actions(self):

        if randint(1, 9) == 1:
            rand_pos_x = [(self.knight.position.x - randint(40, 60)), (self.knight.position.x + randint(40, 60))]
            rand_pos_y = [(self.knight.position.y - randint(40, 60)), (self.knight.position.y + randint(40, 60))]
            self.knight.velocity = Vector2(rand_pos_x[randint(0, 1)], rand_pos_y[randint(0, 1)]) - self.knight.position
        self.knight.heal();

        if self.knight.velocity.length() > 0:
            self.knight.velocity.normalize_ip();
            self.knight.velocity *= self.knight.maxSpeed


    def check_conditions(self):

        # target is gone
        if  self.knight.current_hp >= self.knight.max_hp *5/10:
            
            return "seeking"


        if (self.knight.position - self.knight.move_target.position).length() < 8:

            # continue on path
            if self.current_connection < self.path_length:
                self.knight.move_target.position = self.path[self.current_connection].toNode.position
                self.current_connection += 1
            
            
        return None

    def entry_actions(self):

        nearest_node = self.knight.path_graph.get_nearest_node(self.knight.position)
        furthest_node = get_furthest_node(self.knight, self.knight.position)

        if nearest_node == self.knight.path_graph.nodes[self.knight.base.spawn_node_index]:
            self.path = pathFindAStar(self.knight.graph, \
                                    nearest_node, \
                                    furthest_node)
        else:
            self.path = pathFindAStar(self.knight.path_graph, \
                                    nearest_node, \
                                    self.knight.path_graph.nodes[self.knight.base.spawn_node_index])

        
        self.path_length = len(self.path)

        if (self.path_length > 1):
            self.current_connection = 0
            self.knight.move_target.position = self.path[1].fromNode.position
        if (self.path_length > 0):
            self.current_connection = 0
            self.knight.move_target.position = self.path[0].fromNode.position
        else:
            self.knight.move_target.position = self.knight.path_graph.nodes[self.knight.base.spawn_node_index]


class KnightStateKO_Anything(State):

    def __init__(self, knight):

        State.__init__(self, "ko")
        self.knight = knight

    def do_actions(self):

        return None


    def check_conditions(self):

        # respawned
        if self.knight.current_respawn_time <= 0:
            self.knight.current_respawn_time = self.knight.respawn_time
            self.knight.ko = False
            self.knight.path_graph = self.knight.paths[randint(0, len(self.knight.paths)-1)]
            return "seeking"
            
        return None

    def entry_actions(self):

        self.knight.current_hp = self.knight.max_hp
        self.knight.position = Vector2(self.knight.base.spawn_position)
        self.knight.velocity = Vector2(0, 0)
        self.knight.target = None

        return None
