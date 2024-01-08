# import pygraphviz as pgv
import numpy as np
from collections import deque

C_INTERVAL = 1.7

class FamilyTree:
    def __init__(self, center):
        self.center = center
        self.person_depth = {self.center: 0}
        self.compute_root()
        self.compute_positions()
    
    def compute_root(self):
        queue = [self.center]
        person_depth = self.person_depth
        roots = []
        while queue:
            father = queue[0].father
            mother = queue[0].mother
            if father and mother:
                queue.append(father)
                queue.append(mother)
                person_depth[father] = person_depth[queue[0]] - 1
                person_depth[mother] = person_depth[queue[0]] - 1
            else:
                roots.append((queue[0], person_depth[queue[0]]))
            queue = queue[1:]
        self.person_depth = person_depth
        self.roots = roots
    
    def compute_positions(self):
        roots = self.roots
        person_position_list = []
        node_list = []
        for root in roots:
            person, dep = root
            root_position = (person, (0, 0, -dep))
            person_position, nodes = self.compute_descend_positions(root_position)
            person_position_list.append(person_position)
            node_list.append(nodes)
        self.person_position_list = person_position_list
        
        self.person_position = {}
        self.node_list = set()
        for i, per_pos in enumerate(person_position_list):
            disp_x = 0
            disp_y = 0
            trans = False
            for per, pos in per_pos.items():
                if per in self.person_position:
                    org_pos = self.person_position[per]
                    disp_x = org_pos[0] - pos[0]
                    disp_y = org_pos[1] - pos[1]
                    trans = True
                    break
            if trans:
                for per, pos in per_pos.items():
                    if not per in self.person_position:
                        self.person_position[per] = (pos[0]+disp_x, pos[1]+disp_y, pos[2])
                for node in node_list[i]:
                    node_pos = node["location"]
                    node["location"] = (node_pos[0]+disp_x, node_pos[1]+disp_y, node_pos[2])
            else:
                for per, pos in per_pos.items():
                    if not per in self.person_position:
                        self.person_position[per] = pos
        
            for node in node_list[i]:
                px, py, pz = node["location"]
                rx, ry, rz = node["rotation"]
                sx, sy, sz = node["scale"]
                self.node_list.add((px, py, pz, rx, ry, rz, sx, sy, sz))
                    
    
    def compute_descend_positions(self, root_position):
        queue = [root_position[0]]
        person_position = {root_position[0]: root_position[1]}
        node_list = []
        while queue:
            pos = person_position[queue[0]]
            if queue[0].partner:
                if queue[0].partner.male:
                    res = -1
                else:
                    res = 1                    
                if pos[2] % 2:
                    p_pos = (pos[0]+res, pos[1], pos[2])
                    node_pos = (pos[0]+res/2, pos[1], pos[2])
                    node_rot = (0, np.pi/2, 0)
                else:
                    p_pos = (pos[0], pos[1]+res, pos[2])
                    node_pos = (pos[0], pos[1]+res/2, pos[2])
                    node_rot = (np.pi/2, 0, 0)
                person_position[queue[0].partner] = p_pos
                node_list.append({"location": node_pos, "rotation": node_rot, "scale": (0.05, 0.05, 1.0)})

                queue = queue + queue[0].children
                if len(queue[0].children) > 1:
                    num_children = len(queue[0].children)
                    if pos[2] % 2:
                        node_pos = ((pos[0]+p_pos[0])/2+(num_children-1)/2*C_INTERVAL, pos[1], pos[2]-0.5)
                        node_rot = (0, np.pi/2, 0)
                    else:
                        node_pos = (pos[0], (pos[1]+p_pos[1])/2+(num_children-1)/2*C_INTERVAL, pos[2]-0.5)
                        node_rot = (np.pi/2, 0, 0)
                    node_list.append({"location": node_pos, "rotation": node_rot, "scale": (0.05, 0.05, (num_children-1)*C_INTERVAL)})
                for i, child in enumerate(queue[0].children):
                    c_inteval = C_INTERVAL * i
                    if pos[2] % 2:
                        person_position[child] = ((pos[0]+p_pos[0])/2+c_inteval, pos[1], pos[2]-1)
                    else:
                        person_position[child] = (pos[0], (pos[1]+p_pos[1])/2+c_inteval, pos[2]-1)
                    if i == 0:
                        node_pos = (person_position[child][0], person_position[child][1], pos[2]-0.5)
                        node_rot = (0, 0, 0)
                        node_scale = (0.05, 0.05, 1.0)
                    else:
                        node_pos = (person_position[child][0], person_position[child][1], pos[2]-0.75)
                        node_rot = (0, 0, 0)
                        node_scale = (0.05, 0.05, 0.5)
                    node_list.append({"location": node_pos, "rotation": node_rot, "scale": node_scale})
                queue = queue[1:]
            else:
                queue = queue[1:]
        return person_position, node_list
    
    # def find_siblings(self, person):
    #     if person.father and person.mother:
    #         siblings = person.father.children
    #     else:
    #         siblings = []
    #     return siblings

    # def build_graph(self):
    #     G = pgv.AGraph(directed=True)
    #     self.person_depth = {self.center: 0}
    #     G = self.build_descend(G)
    #     G = self.build_ancestor(G)
    #     return G
    
    # def build_whole_graph(self):
    #     G = pgv.AGraph(directed=True)
    #     self.person_depth = {self.center: 0}
    #     self.build_ancestor(G)
    #     for person, dep in self.roots:
    #         self.center = person
    #         G = self.build_descend(G)
    #     return G
    
    # def build_descend(self, G):
    #     queue = [self.center]
    #     person_depth = self.person_depth
    #     while queue:
    #         if queue[0].partner:
    #             G.add_edge(queue[0].name, queue[0].partner.name)
    #             G.add_edge(queue[0].partner.name, queue[0].name)
    #             person_depth[queue[0].partner] = person_depth[queue[0]]
    #             queue = queue + queue[0].children
    #             for child in queue[0].children:
    #                 G.add_edge(queue[0].name, child.name)
    #                 G.add_edge(queue[0].partner.name, child.name)
    #                 person_depth[child] = person_depth[queue[0]] + 1
    #             queue = queue[1:]
    #         else:
    #             queue = queue[1:]
    #     self.person_depth = person_depth
    #     return G
    
    # def build_ancestor(self, G):
    #     queue = [self.center]
    #     person_depth = self.person_depth
    #     roots = []
    #     while queue:
    #         father = queue[0].father
    #         mother = queue[0].mother
    #         if father and mother:
    #             queue.append(father)
    #             queue.append(mother)
    #             G.add_edge(queue[0].father.name, queue[0].name)
    #             G.add_edge(queue[0].mother.name, queue[0].name)
    #             G.add_edge(queue[0].father.name, queue[0].mother.name)
    #             G.add_edge(queue[0].mother.name, queue[0].father.name)
    #             person_depth[father] = person_depth[queue[0]] - 1
    #             person_depth[mother] = person_depth[queue[0]] - 1
    #         else:
    #             roots.append((queue[0], person_depth[queue[0]]))
    #         queue = queue[1:]
    #     self.person_depth = person_depth
    #     self.roots = roots
    #     return G