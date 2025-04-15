from typing import Dict, Any, Optional

class Event:
    def __init__(self, type: str, data: Optional[Dict[str, Any]] = None) -> None:
        self.type = type
        self.data = data or {}