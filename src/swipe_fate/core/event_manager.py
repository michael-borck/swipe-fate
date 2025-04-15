from typing import Dict, List, Callable, Any
from swipe_fate.core.event import Event

class EventManager:
    def __init__(self) -> None:
        self.listeners: Dict[str, List[Callable]] = {}

    def register_listener(self, event_type: str, listener: Callable) -> None:
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(listener)

    def dispatch_event(self, event: Event) -> None:
        if event.type in self.listeners:
            for listener in self.listeners[event.type]:
                listener(event)