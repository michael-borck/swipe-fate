class ComponentSystem:
    def __init__(self):
        self.components = {}

    def add_component(self, entity_id, component):
        if entity_id not in self.components:
            self.components[entity_id] = []
        self.components[entity_id].append(component)
