from typing import Dict, List, Any

class ComponentSystem:
    def __init__(self) -> None:
        self.components: Dict[str, List[Any]] = {}

    def add_component(self, entity_id: str, component: Any) -> None:
        if entity_id not in self.components:
            self.components[entity_id] = []
        self.components[entity_id].append(component)