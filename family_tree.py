import pygraphviz as pgv
from collections import deque

class FamilyTree:
    def __init__(self, center):
        self.center = center
    
    def build_graph(self):
        self.G = pgv.AGraph(directed=True)
        self.person_depth = {self.center: 0}
        self.build_descend()
        self.build_ancestor()
    
    def build_whole_graph(self):
        self.G = pgv.AGraph(directed=True)
        self.person_depth = {self.center: 0}
        self.build_ancestor()
        for person, dep in self.roots:
            self.center = person
            self.build_descend()
    
    def build_descend(self):
        queue = [self.center]
        person_depth = self.person_depth
        while queue:
            if queue[0].partner:
                self.G.add_edge(queue[0].name, queue[0].partner.name)
                self.G.add_edge(queue[0].partner.name, queue[0].name)
                person_depth[queue[0].partner] = person_depth[queue[0]]
                queue = queue + queue[0].children
                for child in queue[0].children:
                    self.G.add_edge(queue[0].name, child.name)
                    self.G.add_edge(queue[0].partner.name, child.name)
                    person_depth[child] = person_depth[queue[0]] + 1
                # print([q.name for q in queue])
                queue = queue[1:]
            else:
                queue = queue[1:]
        self.person_depth = person_depth
    
    def build_ancestor(self):
        queue = [self.center]
        person_depth = self.person_depth
        roots = []
        while queue:
            father = queue[0].father
            mother = queue[0].mother
            if father and mother:
                queue.append(father)
                queue.append(mother)
                self.G.add_edge(queue[0].father.name, queue[0].name)
                self.G.add_edge(queue[0].mother.name, queue[0].name)
                self.G.add_edge(queue[0].father.name, queue[0].mother.name)
                self.G.add_edge(queue[0].mother.name, queue[0].father.name)
                person_depth[father] = person_depth[queue[0]] - 1
                person_depth[mother] = person_depth[queue[0]] - 1
            else:
                roots.append((queue[0], person_depth[queue[0]]))
            queue = queue[1:]
        self.person_depth = person_depth
        self.roots = roots
    
    def find_siblings(self, person):
        if person.father and person.mother:
            siblings = person.father.children
        else:
            siblings = []
        return siblings
    
    def compute_rank(self):
        pass
    
    def compute_positions(self):
        roots = self.roots
        person_position_list = []
        for root in roots:
            person, dep = root
            root_position = (person, (0, 0, -dep))
            person_position = self.compute_descend_positions(root_position)
            person_position_list.append(person_position)
        self.person_position_list = person_position_list
        
        self.person_position = {}
        for per_pos in person_position_list:
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
            else:
                for per, pos in per_pos.items():
                    if not per in self.person_position:
                        self.person_position[per] = pos
                    
    
    def compute_descend_positions(self, root_position):
        queue = [root_position[0]]
        person_position = {root_position[0]: root_position[1]}
        while queue:
            pos = person_position[queue[0]]
            if queue[0].partner:
                if queue[0].partner.male:
                    res = -1
                else:
                    res = 1                    
                if pos[2] % 2:
                    p_pos = (pos[0]+res, pos[1], pos[2])
                else:
                    p_pos = (pos[0], pos[1]+res, pos[2])
                person_position[queue[0].partner] = p_pos

                queue = queue + queue[0].children
                for i, child in enumerate(queue[0].children):
                    if pos[2] % 2:
                        person_position[child] = ((pos[0]+p_pos[0])/2+i, pos[1], pos[2]-1)
                    else:
                        person_position[child] = (pos[0], (pos[1]+p_pos[1])/2+i, pos[2]-1)
                queue = queue[1:]
            else:
                queue = queue[1:]
        return person_position
