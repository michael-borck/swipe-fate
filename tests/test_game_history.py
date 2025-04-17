import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from swipe_verse.models.game_state import GameState
from swipe_verse.services.game_history import GameHistory


class TestGameHistory(unittest.TestCase):
    """Test the GameHistory class for tracking achievements and game statistics."""

    def setUp(self):
        """Set up a temporary directory for the test."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Patch the home directory to use our temporary directory
        self.home_patcher = patch('pathlib.Path.home')
        self.mock_home = self.home_patcher.start()
        self.mock_home.return_value = Path(self.temp_dir.name)
        
        # Create a GameHistory instance
        self.game_history = GameHistory()
        
        # Create a mock game state for testing
        self.mock_state = MagicMock(spec=GameState)
        self.mock_state.resources = {"treasury": 50, "population": 50, "military": 50, "church": 50}
        self.mock_state.turn_count = 20
        self.mock_state.theme = MagicMock()
        self.mock_state.theme.name = "Kingdom"
        self.mock_state.player_name = "Test Player"
        self.mock_state.difficulty = "normal"

    def tearDown(self):
        """Clean up after the test."""
        self.home_patcher.stop()
        self.temp_dir.cleanup()

    def test_init_creates_directories(self):
        """Test that the GameHistory creates necessary directories."""
        expected_dir = Path(self.temp_dir.name) / ".swipe_verse" / "history"
        self.assertTrue(expected_dir.exists(), "History directory was not created")

    def test_empty_history_on_first_run(self):
        """Test that a new GameHistory has empty history."""
        stats = self.game_history.get_statistics()
        self.assertEqual(stats["total_games"], 0, "New history should have 0 games")
        self.assertEqual(stats["wins"], 0, "New history should have 0 wins")
        self.assertEqual(stats["achievements_unlocked"], 0, 
                         "New history should have 0 unlocked achievements")

    def test_record_game(self):
        """Test recording a game."""
        result = self.game_history.record_game(self.mock_state, won=True, win_message="Victory!")
        
        # Check that the game was recorded
        self.assertEqual(len(self.game_history.history["games"]), 1, "Game was not recorded")
        
        # Check the returned summary
        self.assertEqual(result["game"]["won"], True, "Game result should be a win")
        self.assertEqual(result["game"]["message"], "Victory!", 
                         "Win message not recorded correctly")
        self.assertEqual(result["game"]["theme"], "Kingdom", "Theme not recorded correctly")
        self.assertEqual(result["game"]["turns"], 20, "Turn count not recorded correctly")

    def test_statistics_calculation(self):
        """Test that statistics are calculated correctly."""
        # Record a won game
        self.game_history.record_game(self.mock_state, won=True)
        
        # Record a lost game
        lost_state = MagicMock(spec=GameState)
        lost_state.resources = {"treasury": 10, "population": 10, "military": 10, "church": 10}
        lost_state.turn_count = 10
        lost_state.theme = MagicMock()
        lost_state.theme.name = "Kingdom"
        lost_state.player_name = "Test Player"
        lost_state.difficulty = "normal"
        self.game_history.record_game(lost_state, won=False)
        
        # Check statistics
        stats = self.game_history.get_statistics()
        self.assertEqual(stats["total_games"], 2, "Should have 2 total games")
        self.assertEqual(stats["wins"], 1, "Should have 1 win")
        self.assertEqual(stats["losses"], 1, "Should have 1 loss")
        self.assertEqual(stats["win_percentage"], 50.0, "Win percentage should be 50%")
        self.assertEqual(stats["average_turns"], 20.0, "Average turns should be 20")

    def test_achievement_unlocking(self):
        """Test that achievements are unlocked correctly."""
        # Create a game state that meets the Resource Master achievement condition
        resource_master_state = MagicMock(spec=GameState)
        resource_master_state.resources = {
            "treasury": 95, "population": 50, "military": 50, "church": 50
        }
        resource_master_state.turn_count = 20
        resource_master_state.theme = MagicMock()
        resource_master_state.theme.name = "Kingdom"
        resource_master_state.player_name = "Test Player"
        resource_master_state.difficulty = "normal"
        
        # Record the game
        result = self.game_history.record_game(resource_master_state, won=True)
        
        # Check that the achievement was unlocked
        self.assertEqual(len(result["new_achievements"]), 1, "One achievement should be unlocked")
        self.assertEqual(result["new_achievements"][0]["name"], "Resource Master", 
                         "Resource Master achievement should be unlocked")
        
        # Check that the achievement is marked as unlocked in the game history
        achievements = self.game_history.get_achievements()
        resource_master = next(a for a in achievements if a["name"] == "Resource Master")
        self.assertTrue(resource_master["unlocked"], "Achievement should be marked as unlocked")
        
        # Check no achievements for losing games
        losing_result = self.game_history.record_game(resource_master_state, won=False)
        self.assertEqual(len(losing_result["new_achievements"]), 0, 
                        "No achievements should be unlocked for losing games")

    def test_multiple_achievements(self):
        """Test unlocking multiple achievements at once."""
        # Create a game state that meets multiple achievement conditions
        multi_state = MagicMock(spec=GameState)
        multi_state.resources = {"treasury": 95, "population": 95, "military": 95, "church": 95}
        multi_state.turn_count = 10  # Meets Speed Runner condition
        multi_state.theme = MagicMock()
        multi_state.theme.name = "Kingdom"
        multi_state.player_name = "Test Player"
        multi_state.difficulty = "normal"
        
        # Record the game
        result = self.game_history.record_game(multi_state, won=True)
        
        # Should unlock Resource Master, Speed Runner, and Resource Collector
        self.assertEqual(len(result["new_achievements"]), 3, 
                        "Three achievements should be unlocked")
        
        # Achievement names should be in the result
        achievement_names = [a["name"] for a in result["new_achievements"]]
        self.assertIn("Resource Master", achievement_names)
        self.assertIn("Speed Runner", achievement_names)
        self.assertIn("Resource Collector", achievement_names)
        
    def test_achievements_persistence(self):
        """Test that achievements are persisted between instances."""
        # Unlock an achievement
        resource_master_state = MagicMock(spec=GameState)
        resource_master_state.resources = {
            "treasury": 95, "population": 50, "military": 50, "church": 50
        }
        resource_master_state.turn_count = 20
        resource_master_state.theme = MagicMock()
        resource_master_state.theme.name = "Kingdom"
        resource_master_state.player_name = "Test Player"
        resource_master_state.difficulty = "normal"
        
        self.game_history.record_game(resource_master_state, won=True)
        
        # Create a new GameHistory instance
        new_history = GameHistory()
        
        # Check that the achievement is still unlocked
        achievements = new_history.get_achievements()
        resource_master = next(a for a in achievements if a["name"] == "Resource Master")
        self.assertTrue(resource_master["unlocked"], 
                       "Achievement should remain unlocked in new instance")

    def test_history_limit(self):
        """Test that history is limited to 100 games."""
        # Record 105 games
        for i in range(105):
            self.game_history.record_game(self.mock_state, won=True)
        
        # History should only contain 100 games
        self.assertEqual(len(self.game_history.history["games"]), 100, 
                        "History should be limited to 100 games")
        
    def test_recent_games(self):
        """Test retrieving recent games."""
        # Record 10 games
        for i in range(10):
            self.mock_state.turn_count = i + 1
            self.game_history.record_game(self.mock_state, won=True)
        
        # Get 5 recent games
        recent = self.game_history.get_recent_games(5)
        
        # Should have 5 games
        self.assertEqual(len(recent), 5, "Should retrieve 5 recent games")
        
        # The most recent games should be returned (games 6-10)
        turns = [g["turns"] for g in recent]
        self.assertIn(10, turns, "Should include the last recorded game (turn 10)")
        self.assertIn(9, turns, "Should include the second-to-last recorded game (turn 9)")
        self.assertIn(8, turns, "Should include the third-to-last recorded game (turn 8)")
        self.assertIn(7, turns, "Should include the fourth-to-last recorded game (turn 7)")
        self.assertIn(6, turns, "Should include the fifth-to-last recorded game (turn 6)")
        
        # Games with turns 1-5 should not be included
        for i in range(1, 6):
            self.assertNotIn(i, turns, f"Should not include earlier game with turn {i}")

if __name__ == '__main__':
    unittest.main()