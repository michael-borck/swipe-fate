import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import flet as ft

from swipe_verse.models.config import GameConfig, GameInfo, Theme
from swipe_verse.ui.components.game_selector import GameCard, GameSelector


class TestGameSelector(unittest.TestCase):
    """Test the GameSelector component for the game selection carousel."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock callback
        self.mock_select_game = MagicMock()
        
        # Create mock page
        self.mock_page = MagicMock(spec=ft.Page)
        
        # Create the GameSelector
        self.selector = GameSelector(
            on_select_game=self.mock_select_game,
            width=800
        )

    @patch('swipe_verse.ui.components.game_selector.ConfigLoader')
    def test_init_creates_scroll_container(self, mock_config_loader_cls):
        """Test that the GameSelector initializes with a scroll container."""
        self.assertIsInstance(self.selector.scroll_container, ft.Container)
        self.assertIsInstance(self.selector.scroll_container.content, ft.Row)
        self.assertEqual(self.selector.scroll_container.width, 700)  # 800 - 100 for buttons

    @patch('swipe_verse.ui.components.game_selector.ConfigLoader')
    @patch('swipe_verse.ui.components.game_selector.Path')
    async def test_load_games_loads_configs(self, mock_path, mock_config_loader_cls):
        """Test that load_games loads game configs."""
        # Configure mock config loader
        mock_config_loader = mock_config_loader_cls.return_value
        mock_config_loader.load_config = AsyncMock()
        
        # Create mock config
        mock_config = MagicMock(spec=GameConfig)
        mock_config.theme = MagicMock(spec=Theme)
        mock_config.theme.card_back = "test_card_back.png"
        mock_config.theme.resource_icons = {"resource1": "icon1.png", "resource2": "icon2.png"}
        mock_config.game_info = MagicMock(spec=GameInfo)
        mock_config.game_info.title = "Test Game"
        mock_config.game_info.description = "Test Description"
        mock_config.game_info.backstory = "This is a test game backstory."
        
        mock_config_loader.load_config.return_value = mock_config
        
        # Configure mock Path
        mock_path_instance = MagicMock()
        mock_path.return_value = mock_path_instance
        mock_path_instance.parent.parent.parent = mock_path_instance
        mock_path_instance.__truediv__.return_value = mock_path_instance
        
        # Mock glob to return a list of game files
        mock_path_instance.glob.return_value = [Path("test_game.json")]
        
        # Call load_games
        await self.selector.load_games(self.mock_page)
        
        # Check that load_config was called
        mock_config_loader.load_config.assert_called_once()
        
        # Check that a game card was added
        self.assertEqual(len(self.selector.game_cards), 2)  # 1 game + 1 multiverse portal
        
        # First card should be a GameCard
        self.assertIsInstance(self.selector.game_cards[0], GameCard)

    def test_scroll_left_updates_position(self):
        """Test that _scroll_left updates the scroll position."""
        # Set up a mock row
        mock_row = MagicMock(spec=ft.Row)
        mock_row.scroll_left = 300
        self.selector.scroll_container.content = mock_row
        
        # Call _scroll_left
        self.selector._scroll_left(None)
        
        # Check that scroll_to was called with the correct parameters
        mock_row.scroll_to.assert_called_once_with(
            offset=0,
            duration=300,
            curve=ft.AnimationCurve.EASE_IN_OUT
        )

    def test_scroll_right_updates_position(self):
        """Test that _scroll_right updates the scroll position."""
        # Set up a mock row
        mock_row = MagicMock(spec=ft.Row)
        mock_row.scroll_left = 0
        self.selector.scroll_container.content = mock_row
        self.selector.scroll_container.width = 300
        
        # Add some game cards to calculate max scroll
        self.selector.game_cards = [MagicMock() for _ in range(3)]
        
        # Call _scroll_right
        self.selector._scroll_right(None)
        
        # Check that scroll_to was called with the correct parameters
        mock_row.scroll_to.assert_called_once_with(
            offset=300,
            duration=300,
            curve=ft.AnimationCurve.EASE_IN_OUT
        )

    def test_update_button_visibility(self):
        """Test that _update_button_visibility updates button visibility."""
        # Set up a mock row
        mock_row = MagicMock(spec=ft.Row)
        mock_row.scroll_left = 150  # Middle position
        self.selector.scroll_container.content = mock_row
        self.selector.scroll_container.width = 300
        
        # Add some game cards to calculate max scroll
        self.selector.game_cards = [MagicMock() for _ in range(5)]  # 5 * 300 > 300
        
        # Call _update_button_visibility
        self.selector._update_button_visibility()
        
        # Check that button visibility was updated
        self.assertTrue(self.selector.left_button.visible)
        self.assertTrue(self.selector.right_button.visible)
        
        # Test at start position
        mock_row.scroll_left = 0
        self.selector._update_button_visibility()
        self.assertFalse(self.selector.left_button.visible)
        self.assertTrue(self.selector.right_button.visible)
        
        # Test at end position
        mock_row.scroll_left = 1200  # Max position
        self.selector._update_button_visibility()
        self.assertTrue(self.selector.left_button.visible)
        self.assertFalse(self.selector.right_button.visible)

    def test_add_multiverse_card(self):
        """Test that _add_multiverse_card adds a card for the Multi-Verse Portal."""
        # Set up a mock row
        mock_row = MagicMock(spec=ft.Row)
        mock_row.controls = []
        self.selector.scroll_container.content = mock_row
        self.selector.game_cards = []
        
        # Call _add_multiverse_card
        self.selector._add_multiverse_card()
        
        # Check that a card was added to the row
        self.assertEqual(len(mock_row.controls), 1)
        
        # Check that a card was added to game_cards
        self.assertEqual(len(self.selector.game_cards), 1)
        
        # The card should have a purple background
        portal_card = mock_row.controls[0]
        self.assertTrue("PURPLE" in portal_card.bgcolor.value)
        
        # Should contain "Multi-Verse Portal" text
        text_found = False
        if isinstance(portal_card.content, ft.Column):
            for control in portal_card.content.controls:
                if isinstance(control, ft.Container) and isinstance(control.content, ft.Text):
                    if "Multi-Verse Portal" in control.content.value:
                        text_found = True
                        break
        
        self.assertTrue(text_found, "Card should contain Multi-Verse Portal text")

    @patch('swipe_verse.ui.components.game_selector.asyncio.sleep')
    async def test_reset_portal_animation(self, mock_sleep):
        """Test the _reset_portal_animation method."""
        # Create a mock portal card
        mock_card = MagicMock()
        mock_card.visible = True
        
        # Call _reset_portal_animation
        await self.selector._reset_portal_animation(mock_card, self.mock_page)
        
        # Check that sleep was called
        mock_sleep.assert_called_with(1.5)
        
        # Check that the card's shadow was updated
        self.assertTrue(mock_card.shadow is not None)
        mock_card.update.assert_called_once()


class TestGameCard(unittest.TestCase):
    """Test the GameCard component that displays individual games."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock config
        self.mock_config = MagicMock(spec=GameConfig)
        self.mock_config.theme = MagicMock(spec=Theme)
        self.mock_config.theme.resource_icons = {
            "resource1": "icon1.png", 
            "resource2": "icon2.png",
            "resource3": "icon3.png",
            "resource4": "icon4.png",
            "resource5": "icon5.png"  # More than 4 to test limiting
        }
        self.mock_config.game_info = MagicMock(spec=GameInfo)
        self.mock_config.game_info.title = "Test Game"
        self.mock_config.game_info.description = "Test Description"
        self.mock_config.game_info.backstory = "This is a test game backstory."
        
        # Create mock callback
        self.mock_select = MagicMock()
        
        # Create the GameCard
        self.card = GameCard(
            config_path="test_game.json",
            config=self.mock_config,
            card_back_path="test_card_back.png",
            on_select=self.mock_select
        )

    def test_init_creates_card_content(self):
        """Test that the GameCard initializes with card content."""
        self.assertIsInstance(self.card.content, ft.Column)
        
        # Check that the column has controls
        self.assertTrue(len(self.card.content.controls) > 0)
        
        # Check for title
        title_container = self.card.content.controls[0]
        self.assertIsInstance(title_container, ft.Container)
        self.assertIsInstance(title_container.content, ft.Text)
        self.assertEqual(title_container.content.value, "Test Game")
        
        # Check for description
        description_found = False
        for control in self.card.content.controls:
            if isinstance(control, ft.Container) and isinstance(control.content, ft.Text):
                if control.content.value == "Test Description":
                    description_found = True
                    break
        self.assertTrue(description_found, "Card should contain description")
        
        # Check for backstory
        backstory_found = False
        for control in self.card.content.controls:
            if isinstance(control, ft.Container) and isinstance(control.content, ft.Text):
                if "This is a test game backstory" in control.content.value:
                    backstory_found = True
                    break
        self.assertTrue(backstory_found, "Card should contain backstory")
        
        # Check for button
        button_found = False
        for control in self.card.content.controls:
            if isinstance(control, ft.ElevatedButton):
                button_found = True
                self.assertEqual(control.content.value, "Play This Game")
                break
        self.assertTrue(button_found, "Card should contain play button")

    def test_resource_icons_limited_to_four(self):
        """Test that resource icons are limited to four."""
        # Find the resource row in the card
        resource_row = None
        for control in self.card.content.controls:
            if isinstance(control, ft.Row) and len(control.controls) > 0:
                # This is likely the resource row
                resource_row = control
                break
        
        self.assertIsNotNone(resource_row, "Card should contain resource row")
        
        # Should have 4 resources max
        self.assertEqual(len(resource_row.controls), 4)

    def test_button_calls_on_select(self):
        """Test that the button calls on_select with the config path."""
        # Find the button in the card
        button = None
        for control in self.card.content.controls:
            if isinstance(control, ft.ElevatedButton):
                button = control
                break
        
        self.assertIsNotNone(button, "Card should contain button")
        
        # Trigger the button's on_click
        button.on_click(None)
        
        # Check that on_select was called with the config path
        self.mock_select.assert_called_with("test_game.json")

    def test_long_backstory_truncated(self):
        """Test that long backstory is truncated."""
        # Create a new card with a long backstory
        mock_config = MagicMock(spec=GameConfig)
        mock_config.theme = MagicMock(spec=Theme)
        mock_config.theme.resource_icons = {}
        mock_config.game_info = MagicMock(spec=GameInfo)
        mock_config.game_info.title = "Test Game"
        mock_config.game_info.description = "Test Description"
        mock_config.game_info.backstory = "This is a very long backstory that should be truncated. " * 5
        
        card = GameCard(
            config_path="test_game.json",
            config=mock_config,
            card_back_path="test_card_back.png",
            on_select=self.mock_select
        )
        
        # Check for truncated backstory
        backstory_found = False
        for control in card.content.controls:
            if isinstance(control, ft.Container) and isinstance(control.content, ft.Text):
                if "..." in control.content.value and len(control.content.value) <= 60:
                    backstory_found = True
                    break
        self.assertTrue(backstory_found, "Card should contain truncated backstory")


if __name__ == '__main__':
    unittest.main()