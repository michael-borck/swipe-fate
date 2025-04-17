import unittest
from unittest.mock import MagicMock

import flet as ft

from swipe_verse.services.game_logic import GameLogic
from swipe_verse.ui.achievements_screen import AchievementsScreen


class TestAchievementsScreen(unittest.TestCase):
    """Test the AchievementsScreen UI component."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock game logic
        self.mock_game_logic = MagicMock(spec=GameLogic)
        
        # Set up mock achievements and statistics
        self.mock_achievements = [
            {
                "id": "resource_master",
                "name": "Resource Master",
                "description": "Reach 90+ in any resource",
                "icon": "🏆",
                "unlocked": True
            },
            {
                "id": "balanced_ruler",
                "name": "Balanced Ruler",
                "description": "Keep all resources between 40-60",
                "icon": "⚖️",
                "unlocked": False
            }
        ]
        
        self.mock_statistics = {
            "total_games": 10,
            "wins": 7,
            "losses": 3,
            "win_percentage": 70.0,
            "average_turns": 18.5,
            "best_resources": {"treasury": 85, "population": 90},
            "achievements_unlocked": 1,
            "total_achievements": 2
        }
        
        self.mock_recent_games = [
            {
                "date": "2024-04-17T12:34:56",
                "theme": "Kingdom",
                "player_name": "TestPlayer",
                "turns": 20,
                "resources": {"treasury": 60, "population": 75},
                "difficulty": "normal",
                "won": True,
                "message": "Victory!"
            }
        ]
        
        # Configure mock return values
        self.mock_game_logic.get_achievements.return_value = self.mock_achievements
        self.mock_game_logic.get_statistics.return_value = self.mock_statistics
        self.mock_game_logic.get_recent_games.return_value = self.mock_recent_games
        
        # Create mock callback
        self.mock_back_callback = MagicMock()
        
        # Create achievements screen
        self.screen = AchievementsScreen(
            game_logic=self.mock_game_logic,
            on_back=self.mock_back_callback
        )
        
        # Create mock page
        self.mock_page = MagicMock(spec=ft.Page)
        self.mock_page.width = 800
        self.screen.page = self.mock_page

    def test_build_creates_container(self):
        """Test that build returns a Container."""
        container = self.screen.build()
        self.assertIsInstance(container, ft.Container, "Should return a Container")
        self.assertTrue(container.expand, "Container should expand to fill space")

    def test_achievments_section_shows_unlocked_and_locked(self):
        """Test that achievements are displayed with correct unlock status."""
        container = self.screen.build()
        
        # Extract content from container (this is the main Column)
        main_column = container.content
        self.assertIsInstance(main_column, ft.Column, "Container should contain a Column")
        
        # The second item in the main column contains the achievements section
        achievements_container = main_column.controls[1]
        self.assertIsInstance(achievements_container, ft.Container, "Should have achievements container")
        
        # The achievements container has a Column with achievements
        achievements_column = achievements_container.content
        self.assertIsInstance(achievements_column, ft.Column, "Should have achievements column")
        
        # First element in achievements_column is the achievements header
        achievements_section = achievements_column.controls[0]
        self.assertIsInstance(achievements_section, ft.Column, "Should have achievements section")
        
        # Check for achievement progress text (3rd item in the section)
        progress_text = achievements_section.controls[1]
        self.assertIsInstance(progress_text, ft.Text, "Should have progress text")
        self.assertEqual(progress_text.value, "Unlocked: 1/2", "Should show correct progress")
        
        # Check for achievement cards
        locked_found = False
        unlocked_found = False
        
        # We need to find the achievement cards and check their status
        for i in range(3, len(achievements_section.controls)):
            card = achievements_section.controls[i]
            if isinstance(card, ft.Container) and card.content and isinstance(card.content, ft.Row):
                # Check the achievement lock icon (last item in the row)
                status_container = card.content.controls[-1]
                if isinstance(status_container, ft.Container) and status_container.content:
                    icon = status_container.content
                    if isinstance(icon, ft.Icon):
                        if icon.name == ft.icons.LOCK_OPEN:
                            unlocked_found = True
                        elif icon.name == ft.icons.LOCK:
                            locked_found = True
        
        self.assertTrue(unlocked_found, "Should display an unlocked achievement")
        self.assertTrue(locked_found, "Should display a locked achievement")
    
    def test_statistics_section_shows_game_stats(self):
        """Test that statistics are displayed correctly."""
        container = self.screen.build()
        main_column = container.content
        
        # The second item in the main column contains the achievements and statistics
        content_container = main_column.controls[1]
        content_column = content_container.content
        
        # The second item in the content column is the statistics section
        statistics_section = content_column.controls[2]
        self.assertIsInstance(statistics_section, ft.Column, "Should have statistics section")
        
        # Check for stats cards
        stats_found = False
        resources_found = False
        
        for i in range(2, len(statistics_section.controls)):
            card = statistics_section.controls[i]
            if isinstance(card, ft.Container) and card.content:
                content = card.content
                if isinstance(content, ft.Column) and content.controls:
                    header_text = content.controls[0]
                    if isinstance(header_text, ft.Text):
                        if "Game Statistics" in header_text.value:
                            stats_found = True
                        elif "Best Resource Values" in header_text.value:
                            resources_found = True
        
        self.assertTrue(stats_found, "Should display game statistics")
        self.assertTrue(resources_found, "Should display resource statistics")
    
    def test_back_button_triggers_callback(self):
        """Test that the back button calls the on_back callback."""
        container = self.screen.build()
        main_column = container.content
        
        # The last item in the main column is a row containing the back button
        button_row = main_column.controls[-1]
        self.assertIsInstance(button_row, ft.Row, "Should have button row")
        
        # The row contains a button
        button = button_row.controls[0]
        self.assertIsInstance(button, ft.ElevatedButton, "Should have back button")
        
        # Trigger the button's on_click
        button.on_click(None)
        
        # Check that the callback was called
        self.mock_back_callback.assert_called_once()
    
    def test_mobile_layout_adjustments(self):
        """Test responsive layout adjustments for mobile."""
        # Set a mobile width
        self.mock_page.width = 500
        
        container = self.screen.build()
        
        # Check for mobile-specific padding
        self.assertEqual(container.padding, 20, "Should use smaller padding on mobile")

if __name__ == '__main__':
    unittest.main()