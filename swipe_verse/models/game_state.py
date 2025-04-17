from typing import Any, Dict, Set

from swipe_verse.models.config import Card, GameConfig, GameSettings, Theme


class GameState:
    def __init__(
        self,
        resources: Dict[str, int],
        current_card: Card,
        settings: GameSettings,
        theme: Theme,
        difficulty: str = "standard",
        player_name: str = "Player",
    ):
        # Core game state
        self.resources = resources
        self.current_card = current_card
        self.settings = settings
        self.theme = theme

        # Game progress tracking
        self.turn_count = 0
        self.seen_cards: Set[str] = set()

        # Player settings
        self.difficulty = difficulty
        self.player_name = player_name
        self.active_filter = None  # Current visual filter

        # Additional state fields
        self.game_over = False
        self.end_message = ""

    @classmethod
    def new_game(
        cls,
        config: GameConfig,
        player_name: str = "Player",
        difficulty: str = "standard",
    ) -> "GameState":
        """Create a new game state from configuration"""
        # Initialize resources based on config
        resources = {
            resource_id: value
            for resource_id, value in config.game_settings.initial_resources.items()
        }

        # Get first card (could be random or specific starting card)
        import random

        first_card = random.choice(config.cards)

        # Create new game state
        return cls(
            resources=resources,
            current_card=first_card,
            settings=config.game_settings,
            theme=config.theme,
            difficulty=difficulty,
            player_name=player_name,
        )

    def save_game(self) -> dict:
        """Convert game state to a serializable dictionary for saving"""
        return {
            "resources": self.resources,
            "current_card_id": self.current_card.id,
            "turn_count": self.turn_count,
            "seen_cards": list(self.seen_cards),
            "difficulty": self.difficulty,
            "player_name": self.player_name,
            "active_filter": self.active_filter,
            "game_over": self.game_over,
            "end_message": self.end_message,
        }

    @classmethod
    def load_game(cls, save_data: Dict[str, Any], config: GameConfig) -> "GameState":
        """Load game state from saved data and config"""
        # Find the current card by ID
        current_card = None
        for card in config.cards:
            if card.id == save_data["current_card_id"]:
                current_card = card
                break

        if not current_card:
            # Fallback if card not found
            import random

            current_card = random.choice(config.cards)

        # Create game state
        game_state = cls(
            resources=save_data["resources"],
            current_card=current_card,
            settings=config.game_settings,
            theme=config.theme,
            difficulty=save_data["difficulty"],
            player_name=save_data["player_name"],
        )

        # Restore additional state
        game_state.turn_count = save_data["turn_count"]
        game_state.seen_cards = set(save_data["seen_cards"])
        game_state.game_over = save_data["game_over"]
        game_state.end_message = save_data["end_message"]
        game_state.active_filter = save_data.get("active_filter", None)

        return game_state
