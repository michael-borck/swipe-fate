from typing import Dict, Any, List

class GameState:
    def __init__(self) -> None:
        self.score: int = 0
        self.entities: Dict[str, List[Any]] = {}

    def update(self, changes: Dict[str, Any]) -> None:
        # Update logic here
        pass

    def increment_score(self) -> int:
        self.score += 1
        return self.score
        
    def update_score(self, increment: int) -> None:
        self.score += increment

    def is_game_over(self) -> bool:
        # Determine if the game should end
        return False