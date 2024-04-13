class EventManager:
    def __init__(self):
        self.listeners = {}

    def register_listener(self, event_type, listener):
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(listener)

    def dispatch_event(self, event):
        for listener in self.listeners.get(event.type, []):
            listener.handle_event(event)
