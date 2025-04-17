import re
from typing import Any, Dict, Optional, Tuple

from swipe_verse.models.config import Card, GameConfig
from swipe_verse.models.game_state import GameState
from swipe_verse.services.game_history import GameHistory


class GameResult:
    def __init__(
        self,
        game_over: bool = False,
        message: str = "",
        game_summary: Optional[Dict[str, Any]] = None,
    ):
        self.game_over = game_over
        self.message = message
        self.game_summary = game_summary


class GameLogic:
    def __init__(self, game_state: GameState, config: GameConfig):
        self.game_state = game_state
        self.config = config
        # Set up the expression evaluator for popularity formula
        self.formula_pattern = re.compile(r"(resource\d+)")
        # Initialize game history
        self.history = GameHistory()

    def process_choice(self, direction: str) -> GameResult:
        """Process player's choice (left or right)"""
        current_card = self.game_state.current_card

        if direction not in current_card.choices:
            return GameResult(False, "Invalid choice")

        choice = current_card.choices[direction]

        # Apply effects on resources based on difficulty
        difficulty_mod = self.game_state.settings.difficulty_modifiers[
            self.game_state.difficulty
        ]

        for resource_id, value in choice.effects.items():
            if resource_id in self.game_state.resources:
                # Apply difficulty modifier
                modified_value = int(value * difficulty_mod)

                # Update resource value
                current_value = self.game_state.resources[resource_id]
                new_value = max(0, min(100, current_value + modified_value))
                self.game_state.resources[resource_id] = new_value

        # Increment turn counter
        self.game_state.turn_count += 1

        # Check for game over conditions
        game_over, message, won = self._check_game_over()
        if game_over:
            # Record game in history
            game_summary = self.history.record_game(self.game_state, won, message)
            return GameResult(True, message, game_summary)

        # Find next card
        if choice.next_card:
            self._set_next_card(choice.next_card)
        else:
            self._set_random_card()

        return GameResult(False)

    def calculate_popularity(self) -> int:
        """Calculate popularity based on the formula in config"""
        formula = self.config.game_settings.stats.popularity_formula

        # Replace resource references with actual values
        def replace_resource(match: re.Match) -> str:
            resource_name = match.group(1)
            return str(self.game_state.resources.get(resource_name, 0))

        # Substitute resource placeholders with actual values
        formula_with_values = self.formula_pattern.sub(replace_resource, formula)

        try:
            # Evaluate the formula safely using restricted context
            result = eval(formula_with_values, {"__builtins__": {}})
            # Convert to percentage in 0-100 range
            popularity = max(0, min(100, int(result)))
            return popularity
        except Exception as e:
            print(f"Error evaluating popularity formula: {e}")
            # Default fallback - average of all resources
            if self.game_state.resources:
                return sum(self.game_state.resources.values()) // len(
                    self.game_state.resources
                )
            return 50

    def calculate_progress(self) -> int:
        """Calculate game progress percentage"""
        # This could be based on different factors depending on game design
        # Options:
        # 1. Cards seen / total cards
        # 2. Turns / estimated total turns
        # 3. Story progression markers

        # For now, implement a basic version based on cards seen
        total_cards = len(self.config.cards)
        cards_seen = len(self.game_state.seen_cards)

        # Avoid division by zero
        if total_cards == 0:
            return 0

        progress = min(100, int((cards_seen / total_cards) * 100))
        return progress

    def _check_game_over(self) -> Tuple[bool, str, bool]:
        """
        Check if any game over conditions are met.

        Returns:
            Tuple of (game_over, message, won)
            - game_over: True if game is over
            - message: Description of end condition
            - won: True if player won, False if lost
        """
        # Check resource-based win/lose conditions
        for condition in self.game_state.settings.win_conditions:
            resource_id = condition.resource
            if resource_id in self.game_state.resources:
                value = self.game_state.resources[resource_id]

                # Check if resource is outside allowed range
                if value < condition.min:
                    return True, f"Game over: {resource_id} too low!", False
                if value > condition.max:
                    return True, f"Game over: {resource_id} too high!", False

        # Check victory conditions
        # For now, consider it a win if player survives for 20+ turns
        if self.game_state.turn_count >= 20:
            return (
                True,
                f"Victory! You've ruled successfully for {self.game_state.turn_count} {self.game_state.settings.turn_unit}!",
                True,
            )

        # Could add other game over conditions here
        # - Turn limit reached
        # - Special ending card
        # - Achievement of specific goal

        return False, "", False

    def _set_next_card(self, card_id: str) -> bool:
        """Set the specified card as the next one to display"""
        for card in self.config.cards:
            if card.id == card_id:
                self.game_state.current_card = card
                self.game_state.seen_cards.add(card_id)
                return True

        # If card not found, fall back to random
        self._set_random_card()
        return False

    def _set_random_card(self) -> None:
        """Set a random card from the deck as the next one"""
        import random

        # Filter out cards that require specific conditions
        available_cards = [
            card for card in self.config.cards if self._card_conditions_met(card)
        ]

        if not available_cards:
            # If no cards available, reset seen cards and try again
            self.game_state.seen_cards.clear()
            available_cards = [
                card for card in self.config.cards if self._card_conditions_met(card)
            ]

        if available_cards:
            next_card = random.choice(available_cards)
            self.game_state.current_card = next_card
            self.game_state.seen_cards.add(next_card.id)
        else:
            # This should never happen if there are cards in the config
            raise ValueError("No cards available to display")

    def _card_conditions_met(self, card: Card) -> bool:
        """Check if a card's conditions are met to be displayed"""
        # This could be expanded to check for prerequisites like:
        # - Resource levels
        # - Previous cards seen
        # - Turn number

        # For now, just avoid showing recently seen cards
        return card.id not in self.game_state.seen_cards

    def get_achievements(self) -> list:
        """Get achievements list with unlock status."""
        return self.history.get_achievements()

    def get_statistics(self) -> Dict[str, Any]:
        """Get gameplay statistics."""
        return self.history.get_statistics()

    def get_recent_games(self, limit: int = 5) -> list:
        """Get most recent game records."""
        return self.history.get_recent_games(limit)
