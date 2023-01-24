import pygame

from random import randint, random
from Graph import *

from Character import *
from State import *

from Functions_Anything import *

class Archer_Anything(Character):

    def __init__(self, world, image, projectile_image, base, position):

        Character.__init__(self, world, "archer", image)

        self.projectile_image = projectile_image

        self.graph = Graph(self)
        generate_pathfinding_graphs(self, "pathfinding_graph_Anything.txt")

        self.base = base
        self.position = position
        self.move_target = GameEntity(world, "archer_move_target", None)
        self.target = None

        self.maxSpeed = 50
        self.min_target_distance = 100
        self.projectile_range = 100
        self.projectile_speed = 100

        seeking_state = ArcherStateSeeking_Anything(self)
        attacking_state = ArcherStateAttacking_Anything(self)
        fleeing_state = ArcherStateFleeing_Anything(self)
        ko_state = ArcherStateKO_Anything(self)

        self.brain.add_state(seeking_state)
        self.brain.add_state(attacking_state)
        self.brain.add_state(fleeing_state)
        self.brain.add_state(ko_state)

        self.brain.set_state("seeking")

    def render(self, surface):

        Character.render(self, surface)


    def process(self, time_passed):
        
        Character.process(self, time_passed)
        
        level_up_stats = ["speed", "projectile range"]
        level = 1
        if self.can_level_up():
            if level <= 4:
                choice = 0
            else:
                choice = 1
            self.level_up(level_up_stats[choice])


class ArcherStateSeeking_Anything(State):

    def __init__(self, archer):

        State.__init__(self, "seeking")
        self.archer = archer

        self.archer.path_graph = self.archer.paths[randint(0, len(self.archer.paths)-1)]


    def do_actions(self):

        # move = randint(15,30)
        # lr = randint(1,4)
        # if lr == 1:
        #     #rand_vec = Vector2(self.archer.position[0] + move, self.archer.position[1])
        #     rand_vec = Vector2(randint(60,80), randint(-90,-70))
        #     self.archer.velocity = rand_vec
        # if lr == 2:
        #     #rand_vec = Vector2(self.archer.position[0], self.archer.position[1] + move)
        #     rand_vec = Vector2(randint(-80,-60), randint(70,90))
        #     self.archer.velocity = rand_vec
        # if lr == 3:
        #     #rand_vec = Vector2(self.archer.position[0] - move, self.archer.position[1])
        #     rand_vec = Vector2(randint(60,80), randint(-90,-70))
        #     self.archer.velocity = rand_vec
        # if lr == 4:
        #     #rand_vec = Vector2(self.archer.position[0], self.archer.position[1] - move)
        #     rand_vec = Vector2(randint(-80,-60), randint(70,90))
        #     self.archer.velocity = rand_vec

        self.archer.velocity = self.archer.move_target.position - self.archer.position
        if self.archer.velocity.length() > 0:
            self.archer.velocity.normalize_ip();
            self.archer.velocity *= self.archer.maxSpeed

    def check_conditions(self):

        # check if opponent is in range
        nearest_opponent = self.archer.world.get_nearest_opponent(self.archer)
        if nearest_opponent is not None:
            opponent_distance = (self.archer.position - nearest_opponent.position).length()
            if opponent_distance <= self.archer.min_target_distance:
                    self.archer.target = nearest_opponent
                    return "attacking"
        
        if (self.archer.position - self.archer.move_target.position).length() < 8:

            # continue on path
            if self.current_connection < self.path_length:
                self.archer.move_target.position = self.path[self.current_connection].toNode.position
                self.current_connection += 1
            
        return None

    def entry_actions(self):

        nearest_node = self.archer.path_graph.get_nearest_node(self.archer.position)

        self.path = pathFindAStar(self.archer.path_graph, \
                                  nearest_node, \
                                  self.archer.path_graph.nodes[self.archer.base.target_node_index])

        
        self.path_length = len(self.path)

        if (self.path_length > 0):
            self.current_connection = 0
            self.archer.move_target.position = self.path[0].fromNode.position

        else:
            self.archer.move_target.position = self.archer.path_graph.nodes[self.archer.base.target_node_index].position


class ArcherStateAttacking_Anything(State):

    def __init__(self, archer):

        State.__init__(self, "attacking")
        self.archer = archer

    def do_actions(self):

        opponent_distance = (self.archer.position - self.archer.target.position).length()
        # move = randint(15,30)
        # lr = randint(1,4)
        # if lr == 1:
        #     #rand_vec = Vector2(self.archer.position[0] + move, self.archer.position[1])
        #     rand_vec = Vector2(randint(60,80), randint(-90,-70))
        #     self.archer.velocity = rand_vec
        # if lr == 2:
        #     #rand_vec = Vector2(self.archer.position[0], self.archer.position[1] + move)
        #     rand_vec = Vector2(randint(-80,-60), randint(70,90))
        #     self.archer.velocity = rand_vec
        # if lr == 3:
        #     #rand_vec = Vector2(self.archer.position[0] - move, self.archer.position[1])
        #     rand_vec = Vector2(randint(60,80), randint(-90,-70))
        #     self.archer.velocity = rand_vec
        # if lr == 4:
        #     #rand_vec = Vector2(self.archer.position[0], self.archer.position[1] - move)
        #     rand_vec = Vector2(randint(-80,-60), randint(70,90))
        #     self.archer.velocity = rand_vec

        # opponent within range
    
        
        

    

        if self.archer.pos == 2:
            if randint(1, 4) == 1:
                rand_vec = [Vector2(0, randint(-90,-70)), Vector2(0, randint(70,90))]
                self.archer.velocity = rand_vec[randint(0,1)]
        elif self.archer.pos == 3:
            if randint(1, 4) == 1:
                rand_vec = [Vector2(randint(60,80), 0), Vector2(randint(-80,-60), 0)]
                self.archer.velocity = rand_vec[randint(0,1)]
        else:
            if randint(1, 4) == 1:
                rand_vec = [Vector2(randint(60,80), randint(-90,-70)), Vector2(randint(-80,-60), randint(70,90))]
                self.archer.velocity = rand_vec[randint(0,1)]

        if self.archer.velocity.length() > 0:
            self.archer.velocity.normalize_ip();
            self.archer.velocity *= self.archer.maxSpeed
        
        if self.archer.current_ranged_cooldown <= 0:
            self.archer.ranged_attack(self.archer.target.position)


    def check_conditions(self):
        opponent_distance = (self.archer.position - self.archer.target.position).length()

        # target is gone
        if self.archer.world.get(self.archer.target.id) is None or self.archer.target.ko:
            self.archer.target = None
            return "seeking"

        if opponent_distance > self.archer.min_target_distance:
            self.archer.target = None
            return "seeking"

        if self.archer.target.name == "knight" or self.archer.target.name == "orc":
            if opponent_distance <= 100:
                return "fleeing"
        
        if self.archer.target.name == "wizard":
            if opponent_distance <= 120:
                return "fleeing"

        if 40 <= self.archer.position.x <= 855 and 716 <= self.archer.position.y <= 727:
            self.archer.pos = 2

        if 150 <= self.archer.position.x <= 970 and self.archer.position.y == 50:
            self.archer.pos = 2

        if 40 <= self.archer.position.x <= 44 and 164 <= self.archer.position.y <= 716:
            self.archer.pos = 3

        if self.archer.position.x == 970 and 50 <= self.archer.position.y <= 628:
            self.archer.pos = 3

    def entry_actions(self):

        return None

class ArcherStateFleeing_Anything(State):

    def __init__(self, archer):

        State.__init__(self, "fleeing")
        self.archer = archer

        self.archer.path_graph = self.archer.world.paths[randint(0, len(self.archer.world.paths)-1)]

    def do_actions(self):

        if self.archer.pos == 2:
            if randint(1, 4) == 1:
                rand_vec = [Vector2(0, randint(-90,-70)), Vector2(0, randint(70,90))]
                self.archer.velocity = rand_vec[randint(0,1)]
        elif self.archer.pos == 3:
            if randint(1, 4) == 1:
                rand_vec = [Vector2(randint(60,80), 0), Vector2(randint(-80,-60), 0)]
                self.archer.velocity = rand_vec[randint(0,1)]
        else:
            if randint(1, 4) == 1:
                rand_vec = [Vector2(randint(60,80), randint(-90,-70)), Vector2(randint(-80,-60), randint(70,90))]
                self.archer.velocity = rand_vec[randint(0,1)]
        
        if self.archer.target.name == "wizard" or self.archer.target.name == "archer":
            if randint(1, 4) == 1:
                rand_pos_x = [(self.archer.position.x - randint(40, 60)), (self.archer.position.x + randint(40, 60))]
                rand_pos_y = [(self.archer.position.y - randint(40, 60)), (self.archer.position.y + randint(40, 60))]
                self.archer.velocity = Vector2(rand_pos_x[randint(0, 1)], rand_pos_y[randint(0, 1)]) - self.archer.position
        else:
            self.archer.velocity = self.archer.move_target.position - self.archer.position
        
        if self.archer.current_ranged_cooldown <= 0:
                self.archer.ranged_attack(self.archer.target.position)


    def check_conditions(self):
        opponent_distance = (self.archer.position - self.archer.target.position).length()

        # If target is gone
        if self.archer.world.get(self.archer.target.id) is None or self.archer.target.ko:
            self.archer.target = None
            return "seeking"
            
        # If target is gone from minimum target distance
        if opponent_distance > self.archer.min_target_distance:
            self.archer.target = None
            return "seeking"

        # Defense for knight/orc
        # Return attacking only if there is a distance between knight/orc from archer to avoid getting attacked
        if self.archer.target.name == "knight"or self.archer.target.name == "orc":
            if opponent_distance > 100:
                return "attacking"
        
        if self.archer.target.name == "wizard":
            if opponent_distance > 120:
                return "attacking"

        if 40 <= self.archer.position.x <= 855 and 716 <= self.archer.position.y <= 727:
            self.archer.pos = 2

        if 150 <= self.archer.position.x <= 970 and self.archer.position.y == 50:
            self.archer.pos = 2

        if 40 <= self.archer.position.x <= 44 and 164 <= self.archer.position.y <= 716:
            self.archer.pos = 3

        if self.archer.position.x == 970 and 50 <= self.archer.position.y <= 628:
            self.archer.pos = 3

    
    def entry_actions(self):
        nearest_node = self.archer.path_graph.get_nearest_node(self.archer.position)
        furthest_node = get_furthest_node(self.archer, self.archer.position)

        if nearest_node == self.archer.path_graph.nodes[self.archer.base.spawn_node_index]:
            self.path = pathFindAStar(self.archer.graph, \
                                    nearest_node, \
                                    furthest_node)
        else:
            self.path = pathFindAStar(self.archer.path_graph, \
                                    nearest_node, \
                                    self.archer.path_graph.nodes[self.archer.base.spawn_node_index])

        
        self.path_length = len(self.path)

        if (self.path_length > 1):
            self.current_connection = 0
            self.archer.move_target.position = self.path[1].fromNode.position
        if (self.path_length > 0):
            self.current_connection = 0
            self.archer.move_target.position = self.path[0].fromNode.position
        else:
            self.archer.move_target.position = self.archer.path_graph.nodes[self.archer.base.spawn_node_index]
        
        self.archer.retreat = True
        return None

                    
class ArcherStateKO_Anything(State):

    def __init__(self, archer):

        State.__init__(self, "ko")
        self.archer = archer

    def do_actions(self):

        return None


    def check_conditions(self):

        # respawned
        if self.archer.current_respawn_time <= 0:
            self.archer.current_respawn_time = self.archer.respawn_time
            self.archer.ko = False
            self.archer.path_graph = self.archer.paths[randint(0, len(self.archer.paths)-1)]
            return "seeking"
            
        return None

    def entry_actions(self):

        self.archer.current_hp = self.archer.max_hp
        self.archer.position = Vector2(self.archer.base.spawn_position)
        self.archer.velocity = Vector2(0, 0)
        self.archer.target = None

        return None
