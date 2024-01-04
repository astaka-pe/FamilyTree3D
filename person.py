class Person:
    def __init__(
        self,
        name,
        male=True,
    ):
        self.name = name
        self.male = male
        self.father = None
        self.mother = None
        self.partner = None
        self.children = []
    
    def add_partner(self, partner):
        self.partner = partner
        partner.partner = self
        self.partner.add_children(self.children)
        self.add_children(partner.children)
    
    def add_child(self, child):
        if not child in self.children:
            self.children.append(child)
        if self.male:
            child.father = self
        else:
            child.mother = self
    
    def add_children(self, children):
        for child in children:
            self.add_child(child)
            if self.partner:
                self.partner.add_child(child)