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
        
        # Create card container first
        self.card_container = ft.Container(padding=20, alignment="center")
        
        # Initialize UI manager with our card container
        self.ui_manager = UIManager(self.page, self.game_state, self.card_container)
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
        # Try a different approach - add buttons directly to the page
        print("Showing game selection options...")
        
        # Clear existing content
        self.card_container.content = None
        
        # Create buttons for available configurations
        business_btn = ft.ElevatedButton(
            text="Business Simulator",
            icon="business",
            on_click=lambda e: self.load_configuration("configs/business.json"),
            color="white",
            bgcolor="#4a86e8",
            width=300,
        )
        
        space_btn = ft.ElevatedButton(
            text="Space Explorer",
            icon="rocket_launch",
            on_click=lambda e: self.load_configuration("configs/space_exploration.json"),
            color="white",
            bgcolor="#7b2cbf",
            width=300,
        )
        
        # Create selection UI
        selection_ui = ft.Column([
            ft.Text("Choose a Game", size=24, weight="bold"),
            ft.Text("Select which game you want to play:", size=16),
            ft.Container(height=20),  # Spacer
            business_btn,
            ft.Container(height=10),  # Spacer
            space_btn,
        ],
        alignment="center",
        horizontal_alignment="center",
        spacing=10)
        
        # Add to card container
        self.card_container.content = selection_ui
        self.page.update()
        
    def load_configuration(self, config_path: str) -> None:
        """Load a game configuration file"""
        print(f"Loading configuration from {config_path}...")
        
        # Show a simple loading message
        self.card_container.content = ft.Text("Loading game...", size=20)
        self.page.update()
        
        try:
            # Load the configuration file
            loader = ResourceLoader(config_path)
            self.config_data = loader.data
            
            print(f"Configuration loaded successfully: {len(self.config_data)} entries")
            
            # Initialize the UI with the loaded configuration
            self.ui_manager.initialize_game(self.config_data)
            
            self.page.update()
            print("Game initialized successfully")
        except Exception as e:
            # Show error message
            error_text = f"Error loading game: {str(e)}"
            print(error_text)
            
            self.card_container.content = ft.Column([
                ft.Text("Error Loading Game", size=20, color="red"),
                ft.Text(error_text, size=14),
                ft.ElevatedButton(
                    text="Try Again",
                    on_click=lambda _: self.show_game_selection()
                )
            ])
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