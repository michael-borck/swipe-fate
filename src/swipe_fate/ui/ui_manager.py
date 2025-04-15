import flet as ft
from typing import Dict, Any, Callable, Optional, List
from swipe_fate.core.game_state import GameState
from swipe_fate.core.event import Event
from swipe_fate.ui.decision_card import create_decision_card
from swipe_fate.ui.resource_display import create_resource_display

class UIManager:
    def __init__(self, page: ft.Page, game_state: GameState, card_container: ft.Container = None) -> None:
        self.page = page
        self.game_state = game_state
        
        # Reference to current decision
        self.current_decision: Optional[Dict[str, Any]] = None
        self.decision_index: int = 0
        self.decisions: List[Dict[str, Any]] = []
        
        # UI components
        self.card_container = card_container or ft.Container(padding=20, alignment="center")
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
            content=ft.Text("SwipeFate", size=24, weight="bold", color="white"),
            padding=15,
            bgcolor=self.game_theme.get("accent_color", "#4a86e8"),
            alignment="center",
        )
        
        # Main content
        content = ft.Column([
            # Top section with resources
            ft.Container(
                content=ft.Column([
                    ft.Text("Resources", size=18, weight="bold"),
                    # Resource display will be added here
                    ft.Text("Loading game...", color="black", size=14, italic=True),
                ]),
                padding=10,
            ),
            
            # Middle section with card
            self.card_container,
            
            # Bottom section with game info
            ft.Container(
                content=ft.Column([
                    ft.Text("Click buttons to make decisions", 
                            size=14, 
                            color="#757575",
                            text_align="center"),
                ]),
                padding=10,
                alignment="center",
            ),
        ], alignment="start", expand=True)
        
        # Add all elements to the page
        self.page.add(
            header,
            content,
        )
        
    def initialize_game(self, config_data: Dict[str, Any]) -> None:
        """Initialize the game with configuration data"""
        print("Initializing game with config data...")
        
        # Clear the page first
        self.page.controls.clear()
        self.page.update()
        
        # Add a header
        header = ft.Container(
            content=ft.Text("SwipeFate", size=24, weight="bold", color="white"),
            padding=15,
            bgcolor="#4a86e8",
            alignment="center",
        )
        self.page.add(header)
        
        # Extract configuration sections
        self.resources_config = config_data.get("resources", {})
        self.decisions = config_data.get("decisions", [])
        self.events = config_data.get("events", [])
        self.game_theme = config_data.get("themes", {}).get("default", {})
        
        print(f"Loaded {len(self.decisions)} decisions and {len(self.resources_config)} resources")
        
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
        
        # Add resources section
        resources_header = ft.Text("Resources", size=18, weight="bold")
        self.page.add(resources_header)
        
        # Create resource display
        try:
            resource_display = create_resource_display(
                self.resources_config,
                self.resource_values,
                self.resource_icons,
                width=380,
            )
            self.page.add(resource_display)
            self.resource_container = resource_display
            print("Resource display created")
        except Exception as e:
            error_text = ft.Text(f"Error creating resource display: {str(e)}", color="red")
            self.page.add(error_text)
            print(f"Error creating resource display: {e}")
        
        # Add card container to the page
        self.page.add(self.card_container)
        
        # Add instruction text
        instruction = ft.Text(
            "Click buttons to make decisions", 
            size=14, 
            color="#757575",
            text_align="center"
        )
        self.page.add(instruction)
        
        self.page.update()
        
        # Start the game with the first decision
        try:
            print("Starting game with first decision")
            self.show_next_decision("start")
        except Exception as e:
            error_text = ft.Text(f"Error showing first decision: {str(e)}", color="red")
            self.page.add(error_text)
            self.page.update()
            print(f"Error showing first decision: {e}")
        
    def show_next_decision(self, decision_id: str) -> None:
        """Show the decision with the specified ID"""
        print(f"Showing decision: {decision_id}")
        
        # Find the decision with the given ID
        next_decision = None
        for decision in self.decisions:
            if decision.get("id") == decision_id:
                next_decision = decision
                break
        
        if not next_decision:
            error_msg = f"Decision ID '{decision_id}' not found!"
            print(error_msg)
            
            # Show error in UI
            self.card_container.content = ft.Container(
                content=ft.Column([
                    ft.Text("Error", size=20, color="red"),
                    ft.Text(error_msg)
                ]),
                padding=20,
                bgcolor="#ffebee",
                border=ft.border.all(1, "red"),
                border_radius=5
            )
            self.page.update()
            return
        
        self.current_decision = next_decision
        
        try:
            print(f"Creating decision card for: {decision_id}")
            # Show simple version for debugging
            self.card_container.content = ft.Container(
                content=ft.Column([
                    ft.Text(
                        value=next_decision.get("text", "Decision text missing"), 
                        size=18, 
                        weight="bold",
                        text_align="center"
                    ),
                    ft.Divider(),
                    ft.Text("Options:", size=16),
                    ft.ElevatedButton(
                        text=next_decision.get("left", {}).get("text", "Left option"),
                        on_click=lambda _: self.handle_decision("left"),
                        bgcolor="red"
                    ),
                    ft.ElevatedButton(
                        text=next_decision.get("right", {}).get("text", "Right option"),
                        on_click=lambda _: self.handle_decision("right"),
                        bgcolor="green"
                    )
                ]),
                padding=20,
                bgcolor="white",
                border=ft.border.all(1, "#4a86e8"),
                border_radius=10,
                width=350
            )
            
            print("Decision card created and added to container")
            self.page.update()
        
        except Exception as e:
            error_msg = f"Error creating decision card: {str(e)}"
            print(error_msg)
            
            # Show error in UI
            self.card_container.content = ft.Text(error_msg, color="red")
            self.page.update()
    
    def handle_decision(self, direction: str) -> None:
        """Handle a decision choice (left or right)"""
        print(f"Handling decision: {direction}")
        
        if not self.current_decision:
            print("No current decision!")
            return
        
        try:
            # Get the effects based on direction
            choice = self.current_decision.get(direction, {})
            effects = choice.get("effects", {})
            next_decision_id = choice.get("next", None)
            
            print(f"Choice: {direction}, Effects: {effects}, Next: {next_decision_id}")
            
            # Show a feedback message
            feedback = ft.Text(
                f"You chose: {choice.get('text', direction.capitalize())}",
                size=16,
                color="blue"
            )
            self.card_container.content = ft.Container(
                content=feedback,
                padding=20,
                bgcolor="#e3f2fd",
                border_radius=10
            )
            self.page.update()
            
            # Apply resource effects
            for resource_id, change in effects.items():
                if resource_id in self.resource_values:
                    print(f"Changing {resource_id} by {change}")
                    self.resource_values[resource_id] += change
                    
                    # Ensure value is within min/max bounds
                    if resource_id in self.resources_config:
                        min_val = self.resources_config[resource_id].get("min", 0)
                        max_val = self.resources_config[resource_id].get("max", 100)
                        self.resource_values[resource_id] = max(
                            min_val, min(max_val, self.resource_values[resource_id])
                        )
            
            # Find the resources section and update it
            for i, control in enumerate(self.page.controls):
                if isinstance(control, ft.Text) and control.value == "Resources":
                    # The next control should be the resource display
                    if i+1 < len(self.page.controls):
                        # Create new resource display
                        try:
                            resource_display = create_resource_display(
                                self.resources_config,
                                self.resource_values,
                                self.resource_icons,
                                width=380,
                            )
                            # Replace the old one
                            self.page.controls[i+1] = resource_display
                            self.page.update()
                            print("Resource display updated")
                        except Exception as e:
                            print(f"Error updating resources: {e}")
                    break
            
            # Check for game over condition
            if self.check_game_over():
                self.show_game_over()
                return
                
            # Show the next decision after a short delay
            if next_decision_id:
                print(f"Will show next decision: {next_decision_id} after delay")
                self.page.after(1000, lambda: self.show_next_decision(next_decision_id))
                
        except Exception as e:
            error_msg = f"Error handling decision: {str(e)}"
            print(error_msg)
            self.card_container.content = ft.Text(error_msg, color="red")
            self.page.update()
    
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