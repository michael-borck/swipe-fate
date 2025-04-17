import json
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, TypedDict, cast

from swipe_verse.models.game_state import GameState


class AchievementDef(TypedDict):
    """TypedDict for achievement definitions"""

    name: str
    description: str
    icon: str
    conditions: Callable[[GameState], bool]
    unlocked: bool


class GameHistory:
    """Manages the history of games played and tracks achievements."""

    def __init__(self) -> None:
        # Create storage directory
        self.storage_dir = Path.home() / ".swipe_verse" / "history"
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Path to main history file
        self.history_file = self.storage_dir / "game_history.json"

        # Load existing history or create empty history
        self.history = self._load_history()

        # Define achievements
        self.achievements: Dict[str, AchievementDef] = {
            "resource_master": {
                "name": "Resource Master",
                "description": "Reach 90+ in any resource",
                "icon": "🏆",
                "conditions": lambda state: any(
                    val >= 90 for val in state.resources.values()
                ),
                "unlocked": False,
            },
            "balanced_ruler": {
                "name": "Balanced Ruler",
                "description": "Keep all resources between 40-60",
                "icon": "⚖️",
                "conditions": lambda state: all(
                    40 <= val <= 60 for val in state.resources.values()
                ),
                "unlocked": False,
            },
            "speed_runner": {
                "name": "Speed Runner",
                "description": "Win the game in 15 turns or less",
                "icon": "⚡",
                "conditions": lambda state: state.turn_count <= 15,
                "unlocked": False,
            },
            "survivalist": {
                "name": "Survivalist",
                "description": "Survive for at least 30 turns",
                "icon": "🛡️",
                "conditions": lambda state: state.turn_count >= 30,
                "unlocked": False,
            },
            "resource_collector": {
                "name": "Resource Collector",
                "description": "Accumulate a total of 300+ resources",
                "icon": "💰",
                "conditions": lambda state: sum(state.resources.values()) >= 300,
                "unlocked": False,
            },
        }

        # Load unlocked achievements
        self._load_achievements()

    def _load_history(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load game history from storage."""
        if not self.history_file.exists():
            return {"games": []}

        try:
            with open(self.history_file, "r") as f:
                # json.load returns Any; cast to expected history format
                return cast(Dict[str, List[Dict[str, Any]]], json.load(f))
        except (json.JSONDecodeError, FileNotFoundError):
            return {"games": []}

    def _save_history(self) -> None:
        """Save game history to storage."""
        with open(self.history_file, "w") as f:
            json.dump(self.history, f, indent=2)

    def _load_achievements(self) -> None:
        """Load unlocked achievements from storage."""
        achievements_file = self.storage_dir / "achievements.json"

        if not achievements_file.exists():
            return

        try:
            with open(achievements_file, "r") as f:
                unlocked = json.load(f)

                # Update unlocked status in achievements dictionary
                for ach_id, is_unlocked in unlocked.items():
                    if ach_id in self.achievements:
                        self.achievements[ach_id]["unlocked"] = is_unlocked
        except (json.JSONDecodeError, FileNotFoundError):
            pass

    def _save_achievements(self) -> None:
        """Save unlocked achievements to storage."""
        achievements_file = self.storage_dir / "achievements.json"

        # Create dictionary of achievement IDs and their unlocked status
        unlocked = {
            ach_id: ach["unlocked"] for ach_id, ach in self.achievements.items()
        }

        with open(achievements_file, "w") as f:
            json.dump(unlocked, f, indent=2)

    def record_game(
        self, game_state: GameState, won: bool, win_message: str = ""
    ) -> Dict[str, Any]:
        """
        Record a completed game in the history.

        Args:
            game_state: The final game state
            won: Whether the player won the game
            win_message: Message describing the win/loss condition

        Returns:
            Dict containing new achievements and game summary
        """
        # Create a game record
        game_record = {
            "date": datetime.now().isoformat(),
            "theme": game_state.theme.name
            if hasattr(game_state.theme, "name")
            else "Unknown",
            "player_name": game_state.player_name,
            "turns": game_state.turn_count,
            "resources": dict(game_state.resources),
            "difficulty": game_state.difficulty,
            "won": won,
            "message": win_message,
        }

        # Add to history
        self.history["games"].append(game_record)

        # Limit history size to 100 games
        if len(self.history["games"]) > 100:
            self.history["games"] = self.history["games"][-100:]

        # Save updated history
        self._save_history()

        # Check for new achievements
        new_achievements = self._check_achievements(game_state, won)

        # Save updated achievements
        self._save_achievements()

        # Return game summary with achievements
        return {
            "game": game_record,
            "new_achievements": new_achievements,
            "statistics": self.get_statistics(),
        }

    def _check_achievements(
        self, game_state: GameState, won: bool
    ) -> List[Dict[str, Any]]:
        """Check if new achievements have been unlocked."""
        if not won:
            return []  # Only check achievements for won games

        new_achievements = []

        for ach_id, achievement in self.achievements.items():
            if not achievement["unlocked"] and achievement["conditions"](game_state):
                # Unlock achievement
                achievement["unlocked"] = True
                new_achievements.append(
                    {
                        "id": ach_id,
                        "name": achievement["name"],
                        "description": achievement["description"],
                        "icon": achievement["icon"],
                    }
                )

        return new_achievements

    def get_statistics(self) -> Dict[str, Any]:
        """Get overall game statistics."""
        games = self.history["games"]

        if not games:
            return {
                "total_games": 0,
                "wins": 0,
                "losses": 0,
                "win_percentage": 0,
                "average_turns": 0,
                "best_resources": {},
                "achievements_unlocked": 0,
            }

        # Calculate statistics
        total_games = len(games)
        wins = sum(1 for game in games if game["won"])
        losses = total_games - wins
        win_percentage = (wins / total_games) * 100 if total_games > 0 else 0

        # Average turns for completed games
        completed_games = [game for game in games if game["won"]]
        average_turns = (
            sum(game["turns"] for game in completed_games) / len(completed_games)
            if completed_games
            else 0
        )

        # Find best resource values
        best_resources: Dict[str, int] = {}
        for game in games:
            for resource, value in game["resources"].items():
                if resource not in best_resources or value > best_resources[resource]:
                    best_resources[resource] = value

        # Count unlocked achievements
        achievements_unlocked = sum(
            1 for ach in self.achievements.values() if ach["unlocked"]
        )

        return {
            "total_games": total_games,
            "wins": wins,
            "losses": losses,
            "win_percentage": round(win_percentage, 1),
            "average_turns": round(average_turns, 1),
            "best_resources": best_resources,
            "achievements_unlocked": achievements_unlocked,
            "total_achievements": len(self.achievements),
        }

    def get_achievements(self) -> List[Dict[str, Any]]:
        """Get list of all achievements with their unlock status."""
        return [
            {
                "id": ach_id,
                "name": ach["name"],
                "description": ach["description"],
                "icon": ach["icon"],
                "unlocked": ach["unlocked"],
            }
            for ach_id, ach in self.achievements.items()
        ]

    def get_recent_games(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get most recent games from history."""
        games = self.history["games"]
        return games[-limit:] if games else []
