import flet as ft
from typing import Dict, Any, Callable, Optional, List
from swipe_fate.core.game_state import GameState
from swipe_fate.core.event import Event
from swipe_fate.ui.decision_card import create_decision_card
from swipe_fate.ui.resource_display import create_resource_display

class UIManager:
    def __init__(self, page: ft.Page, game_state: GameState) -> None:
        self.page = page
        self.game_state = game_state
        
        # Reference to current decision
        self.current_decision: Optional[Dict[str, Any]] = None
        self.decision_index: int = 0
        self.decisions: List[Dict[str, Any]] = []
        
        # UI components
        self.card_container = ft.Container(padding=20, alignment="center")
        self.resource_container = ft.Container()
        self.game_over_dialog: Optional[ft.AlertDialog] = None
        
        # Application state
        self.resources_config: Dict[str, Dict[str, Any]] = {}
        self.resource_values: Dict[str, int] = {}
        self.resource_icons: Dict[str, Dict[str, str]] = {}
        self.game_theme: Dict[str, Any] = {}
        
    def setup_ui(self) -> None:
        """Set up the main UI layout"""
        # Set page properties
        self.page.title = "SwipeFate"
        self.page.padding = 0
        self.page.bgcolor = self.game_theme.get("background_color", "#f0f0f0")
        self.page.window_width = 400
        self.page.window_height = 700
        
        # Header with game title
        header = ft.Container(
            content=ft.Text("SwipeFate", size=24, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
            padding=15,
            bgcolor=self.game_theme.get("accent_color", "#4a86e8"),
            alignment=ft.alignment.center,
        )
        
        # Main content
        content = ft.Column([
            # Top section with resources
            ft.Container(
                content=ft.Column([
                    ft.Text("Resources", size=18, weight=ft.FontWeight.BOLD),
                    # Resource display will be added here
                ]),
                padding=10,
            ),
            
            # Middle section with card
            self.card_container,
            
            # Bottom section with game info
            ft.Container(
                content=ft.Column([
                    ft.Text("Swipe left or right to make decisions", 
                            size=14, 
                            color=ft.colors.BLACK54,
                            text_align=ft.TextAlign.CENTER),
                ]),
                padding=10,
                alignment=ft.alignment.center,
            ),
        ], alignment=ft.MainAxisAlignment.START, expand=True)
        
        # Add all elements to the page
        self.page.add(
            header,
            content,
        )
        
    def initialize_game(self, config_data: Dict[str, Any]) -> None:
        """Initialize the game with configuration data"""
        # Extract configuration sections
        self.resources_config = config_data.get("resources", {})
        self.decisions = config_data.get("decisions", [])
        self.events = config_data.get("events", [])
        self.game_theme = config_data.get("themes", {}).get("default", {})
        
        # Initialize resource values
        self.resource_values = {}
        for resource_id, resource_info in self.resources_config.items():
            self.resource_values[resource_id] = resource_info.get("initial", 0)
        
        # Get resource icons if available
        self.resource_icons = {}
        assets = config_data.get("assets", {})
        if "icons" in assets:
            self.resource_icons = assets.get("icons", {})
        
        # Update page background based on theme
        self.page.bgcolor = self.game_theme.get("background_color", "#f0f0f0")
        
        # Create resource display
        resource_display = create_resource_display(
            self.resources_config,
            self.resource_values,
            self.resource_icons,
            width=380,
        )
        
        # Insert resource display into the UI
        if self.page.controls and len(self.page.controls) > 1:
            resources_container = self.page.controls[1].content.controls[0]
            if len(resources_container.content.controls) > 1:
                resources_container.content.controls[1] = resource_display
            else:
                resources_container.content.controls.append(resource_display)
                
        # Update our reference
        self.resource_container = resource_display
        
        # Start the game with the first decision
        self.show_next_decision("start")
        
    def show_next_decision(self, decision_id: str) -> None:
        """Show the decision with the specified ID"""
        # Find the decision with the given ID
        next_decision = None
        for decision in self.decisions:
            if decision.get("id") == decision_id:
                next_decision = decision
                break
        
        if not next_decision:
            print(f"Decision ID '{decision_id}' not found!")
            return
        
        self.current_decision = next_decision
        
        # Create the decision card
        decision_card = create_decision_card(
            next_decision,
            on_swipe_left=lambda: self.handle_decision("left"),
            on_swipe_right=lambda: self.handle_decision("right"),
        )
        
        # Update the card container
        self.card_container.content = decision_card
        self.page.update()
    
    def handle_decision(self, direction: str) -> None:
        """Handle a decision choice (left or right)"""
        if not self.current_decision:
            return
        
        # Get the effects based on direction
        choice = self.current_decision.get(direction, {})
        effects = choice.get("effects", {})
        next_decision_id = choice.get("next", None)
        
        # Apply resource effects
        for resource_id, change in effects.items():
            if resource_id in self.resource_values:
                self.resource_values[resource_id] += change
                
                # Ensure value is within min/max bounds
                if resource_id in self.resources_config:
                    min_val = self.resources_config[resource_id].get("min", 0)
                    max_val = self.resources_config[resource_id].get("max", 100)
                    self.resource_values[resource_id] = max(
                        min_val, min(max_val, self.resource_values[resource_id])
                    )
        
        # Update the resource display by recreating it
        resource_display = create_resource_display(
            self.resources_config,
            self.resource_values,
            self.resource_icons,
            width=380,
        )
        
        # Replace the old display
        if self.page.controls and len(self.page.controls) > 1:
            resources_container = self.page.controls[1].content.controls[0]
            if len(resources_container.content.controls) > 1:
                resources_container.content.controls[1] = resource_display
            
        # Update our reference
        self.resource_container = resource_display
        
        # Check for game over condition
        if self.check_game_over():
            self.show_game_over()
            return
            
        # Show the next decision after a short delay
        if next_decision_id:
            self.page.after(1000, lambda: self.show_next_decision(next_decision_id))
    
    def check_game_over(self) -> bool:
        """Check if the game has ended"""
        # Game over if any critical resource is at 0
        for resource_id, value in self.resource_values.items():
            # For now, we'll assume the game is over if any resource reaches its minimum
            if resource_id in self.resources_config:
                min_val = self.resources_config[resource_id].get("min", 0)
                if value <= min_val and resource_id in ["fuel", "oxygen", "money"]:
                    return True
        
        return False
    
    def show_game_over(self) -> None:
        """Show game over screen"""
        # Create a game over dialog
        self.game_over_dialog = ft.AlertDialog(
            title=ft.Text("Game Over"),
            content=ft.Column([
                ft.Text("Your journey has ended."),
                ft.Text("Final resources:"),
                *[
                    ft.Text(f"{self.resources_config[r].get('display_name', r)}: {v}")
                    for r, v in self.resource_values.items()
                ],
            ], tight=True),
            actions=[
                ft.TextButton("Play Again", on_click=self.restart_game),
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
        )
        
        # Show the dialog
        self.page.dialog = self.game_over_dialog
        self.game_over_dialog.open = True
        self.page.update()
    
    def restart_game(self, e: ft.ControlEvent) -> None:
        """Restart the game"""
        # Close the dialog
        if self.game_over_dialog:
            self.game_over_dialog.open = False
            self.page.update()
        
        # Reset resource values
        for resource_id, resource_info in self.resources_config.items():
            self.resource_values[resource_id] = resource_info.get("initial", 0)
        
        # Update the resource display by recreating it
        resource_display = create_resource_display(
            self.resources_config,
            self.resource_values,
            self.resource_icons,
            width=380,
        )
        
        # Replace the old display
        if self.page.controls and len(self.page.controls) > 1:
            resources_container = self.page.controls[1].content.controls[0]
            if len(resources_container.content.controls) > 1:
                resources_container.content.controls[1] = resource_display
            
        # Update our reference
        self.resource_container = resource_display
        
        # Start with the first decision
        self.show_next_decision("start")