import flet as ft
from typing import List, Dict, Any, Optional

from swipe_fate.core.game_state import GameState
from swipe_fate.ui.ui_manager import UIManager
from swipe_fate.core.event_manager import EventManager
from swipe_fate.core.event import Event
from swipe_fate.resource_loader import ResourceLoader

class CoreEngine:
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.game_state = GameState()
        self.ui_manager = UIManager(self.page, self.game_state)
        self.event_manager = EventManager()
        self.config_data: Dict[str, Any] = {}
        self.setup()

    def setup(self) -> None:
        """Initialize the game engine"""
        # Set up basic UI structure
        self.ui_manager.setup_ui()
        
        # Register event listeners
        self.event_manager.register_listener("resource_changed", self.handle_resource_changed)
        
        # Show game selection dialog
        self.show_game_selection()
        
    def show_game_selection(self) -> None:
        """Show dialog to select a game configuration"""
        # Create buttons for available configurations
        business_btn = ft.ElevatedButton(
            "Business Simulator",
            icon=ft.icons.BUSINESS,
            on_click=lambda _: self.load_configuration("configs/business.json")
        )
        
        space_btn = ft.ElevatedButton(
            "Space Explorer",
            icon=ft.icons.ROCKET_LAUNCH,
            on_click=lambda _: self.load_configuration("configs/space_exploration.json")
        )
        
        # Create the dialog
        dialog = ft.AlertDialog(
            title=ft.Text("Choose a Game"),
            content=ft.Column([
                ft.Text("Select which game you want to play:"),
                business_btn,
                space_btn,
            ], tight=True, spacing=20),
        )
        
        # Show the dialog
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
        
    def load_configuration(self, config_path: str) -> None:
        """Load a game configuration file"""
        # Close the dialog if it's open
        if self.page.dialog and self.page.dialog.open:
            self.page.dialog.open = False
            self.page.update()
        
        # Load the configuration file
        loader = ResourceLoader(config_path)
        self.config_data = loader.data
        
        # Initialize the UI with the loaded configuration
        self.ui_manager.initialize_game(self.config_data)
        
        self.page.update()
    
    def handle_resource_changed(self, event: Event) -> None:
        """Handle resource changed events"""
        # Update the game state
        if event.data and "resource_id" in event.data and "value" in event.data:
            resource_id = event.data["resource_id"]
            value = event.data["value"]
            # Update the game state (though currently our UI handles this directly)
            pass
    
    def run(self) -> None:
        """Start the game"""
        self.page.update()