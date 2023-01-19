import pygame

from random import randint, random
from Graph import *

def generate_pathfinding_graphs(self, filename):

    f = open(filename, "r")

    # Create the nodes
    line = f.readline()
    while line != "connections\n":
        data = line.split()
        self.graph.nodes[int(data[0])] = Node(self.graph, int(data[0]), int(data[1]), int(data[2]))
        line = f.readline()

    # Create the connections
    line = f.readline()
    while line != "paths\n":
        data = line.split()
        node0 = int(data[0])
        node1 = int(data[1])
        distance = (Vector2(self.graph.nodes[node0].position) - Vector2(self.graph.nodes[node1].position)).length()
        self.graph.nodes[node0].addConnection(self.graph.nodes[node1], distance)
        self.graph.nodes[node1].addConnection(self.graph.nodes[node0], distance)
        line = f.readline()

    # Create the orc paths, which are also Graphs
    self.paths = []
    line = f.readline()
    while line != "":
        path = Graph(self)
        data = line.split()
        
        # Create the nodes
        for i in range(0, len(data)):
            node = self.graph.nodes[int(data[i])]
            path.nodes[int(data[i])] = Node(path, int(data[i]), node.position[0], node.position[1])

        # Create the connections
        for i in range(0, len(data)-1):
            node0 = int(data[i])
            node1 = int(data[i + 1])
            distance = (Vector2(self.graph.nodes[node0].position) - Vector2(self.graph.nodes[node1].position)).length()
            path.nodes[node0].addConnection(path.nodes[node1], distance)
            path.nodes[node1].addConnection(path.nodes[node0], distance)
            
        self.paths.append(path)

        line = f.readline()

    f.close()

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