"""
SwipeFate - A card-based decision game with swipe mechanics
"""
import flet as ft
import os
import sys
import json
import re
from typing import Dict, Any, List, Optional

class SimpleGameUI:
    """Simple UI implementation for SwipeFate that works on all Flet versions"""
    
    def __init__(self, page: ft.Page):
        """Initialize the game UI"""
        self.page = page
        self.setup_page()
        
        # Game state
        self.game_data = {}
        self.decisions = []
        self.current_decision = None
        self.resources = {}
        self.resource_values = {}
        
        # Show game selection
        self.show_game_selection()
        
    def setup_page(self):
        """Set up page properties"""
        self.page.title = "SwipeFate"
        self.page.bgcolor = "#f0f0f0"
        self.page.padding = 10
        self.page.window_width = 400
        self.page.window_height = 800
        self.page.window_resizable = True
        
    def show_game_selection(self):
        """Show the game selection screen"""
        self.page.controls.clear()
        
        # Create header
        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text("SwipeFate", size=24, weight="bold", color="white"),
                    ft.IconButton(
                        icon=ft.icons.HOME,
                        icon_color="white",
                        on_click=lambda _: self.show_game_selection()
                    )
                ],
                alignment="spaceBetween"
            ),
            bgcolor="#2196f3",
            padding=15
        )
        
        # Create selection buttons
        business_card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.icons.BUSINESS, size=30, color="#2196f3"),
                            ft.Text("Startup Simulator", size=20, weight="bold")
                        ],
                        spacing=10
                    ),
                    ft.Text(
                        "Build your startup from zero to IPO",
                        size=14,
                        color="#757575"
                    )
                ]
            ),
            padding=20,
            margin=10,
            bgcolor="white",
            border_radius=5,
            on_click=lambda _: self.load_game("configs/business.json")
        )
        
        space_card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(ft.icons.ROCKET_LAUNCH, size=30, color="#9c27b0"),
                            ft.Text("Space Explorer", size=20, weight="bold")
                        ],
                        spacing=10
                    ),
                    ft.Text(
                        "Survive the dangers of deep space exploration",
                        size=14,
                        color="#757575"
                    )
                ]
            ),
            padding=20,
            margin=10,
            bgcolor="white",
            border_radius=5,
            on_click=lambda _: self.load_game("configs/space_exploration.json")
        )
        
        self.page.add(
            header,
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(
                            "Choose Your Adventure",
                            size=28,
                            weight="bold",
                            text_align="center"
                        ),
                        ft.Text(
                            "Select a game to begin your journey",
                            size=16,
                            color="#757575",
                            text_align="center"
                        ),
                        business_card,
                        space_card
                    ],
                    spacing=20,
                    horizontal_alignment="center"
                ),
                padding=30,
                alignment="center"
            )
        )
        
        self.page.update()
    
    def load_game(self, config_file: str):
        """Load a game configuration file"""
        try:
            # Clear previous game content
            self.page.controls.clear()
            
            # Show loading indicator
            self.page.add(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.ProgressRing(),
                            ft.Text("Loading game...", size=20)
                        ],
                        alignment="center",
                        horizontal_alignment="center"
                    ),
                    alignment="center",
                    expand=True
                )
            )
            self.page.update()
            
            # Read config file
            with open(config_file, "r") as f:
                file_content = f.read()
            
            # Pre-process to handle + and - signs
            clean_content = re.sub(r'(\s+)"(\w+)":\s*\+(\d+)', r'\1"\2": \3', file_content)
            clean_content = re.sub(r'(\s+)"(\w+)":\s*\-(\d+)', r'\1"\2": -\3', clean_content)
            
            # Parse JSON
            self.game_data = json.loads(clean_content)
            
            # Extract game data
            self.decisions = self.game_data.get("decisions", [])
            self.resources = self.game_data.get("resources", {})
            
            # Initialize resource values
            self.resource_values = {}
            for resource_id, resource_info in self.resources.items():
                self.resource_values[resource_id] = resource_info.get("initial", 0)
            
            # Create game UI
            header = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Text("SwipeFate", size=24, weight="bold", color="white"),
                        ft.IconButton(
                            icon=ft.icons.HOME,
                            icon_color="white",
                            on_click=lambda _: self.show_game_selection()
                        )
                    ],
                    alignment="spaceBetween"
                ),
                bgcolor="#2196f3",
                padding=15
            )
            
            self.page.controls.clear()
            
            # Create main page layout
            self.page.add(
                header,
                ft.Divider(height=1, color="#cccccc"),
                self._create_resource_display()
            )
            
            # Start with first decision
            self.show_decision("start")
        
        except Exception as e:
            self.show_error(f"Error loading game: {str(e)}")
    
    def _create_resource_display(self):
        """Create the resource display section"""
        resource_column = ft.Column(spacing=5)
        
        for resource_id, resource_info in self.resources.items():
            value = self.resource_values.get(resource_id, 0)
            display_name = resource_info.get("display_name", resource_id.title())
            
            resource_row = ft.Row(
                controls=[
                    ft.Text(f"{display_name}:", size=14),
                    ft.Text(f"{value}", size=14, weight="bold")
                ],
                alignment="spaceBetween"
            )
            
            resource_column.controls.append(resource_row)
        
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Resources", size=16, weight="bold"),
                    resource_column
                ]
            ),
            padding=10,
            margin=10,
            bgcolor="white",
            border_radius=5,
            border=ft.border.all(1, "#cccccc")
        )
    
    def update_resource_display(self):
        """Update the resource display with current values"""
        resource_display = self._create_resource_display()
        
        # Replace the resource display in the page
        for i, control in enumerate(self.page.controls):
            if i == 2:  # The resource display is the third element
                self.page.controls[i] = resource_display
                break
        
        self.page.update()
    
    def show_decision(self, decision_id: str):
        """Show a decision card"""
        # Find the decision
        decision = None
        for d in self.decisions:
            if d.get("id") == decision_id:
                decision = d
                break
        
        if not decision:
            self.show_error(f"Decision with ID '{decision_id}' not found")
            return
        
        self.current_decision = decision
        
        # Extract decision data
        decision_text = decision.get("text", "Make a decision")
        left_option = decision.get("left", {}).get("text", "Left option")
        right_option = decision.get("right", {}).get("text", "Right option")
        image_url = decision.get("image_url", None)
        
        # Create decision card
        card_content = []
        
        # Add image if available
        if image_url:
            card_content.append(
                ft.Image(
                    src=image_url,
                    width=350,
                    height=200,
                    fit="cover"
                )
            )
        
        # Add decision text
        card_content.append(
            ft.Container(
                content=ft.Text(
                    value=decision_text,
                    size=20,
                    weight="bold",
                    text_align="center"
                ),
                padding=15
            )
        )
        
        # Add buttons
        card_content.append(
            ft.Row(
                controls=[
                    ft.ElevatedButton(
                        text=left_option,
                        on_click=lambda _: self.handle_decision("left"),
                        bgcolor="#f44336",
                        color="white",
                        expand=1
                    ),
                    ft.ElevatedButton(
                        text=right_option,
                        on_click=lambda _: self.handle_decision("right"),
                        bgcolor="#4caf50",
                        color="white",
                        expand=1
                    )
                ],
                spacing=10,
                alignment="center"
            )
        )
        
        # Create the card
        decision_card = ft.Card(
            content=ft.Column(
                controls=card_content,
                horizontal_alignment="center"
            ),
            width=350,
            elevation=5,
            margin=10
        )
        
        # Add or replace the decision card
        if len(self.page.controls) > 3:
            self.page.controls.pop()  # Remove previous card if exists
        
        self.page.add(
            ft.Container(
                content=decision_card,
                alignment="center",
                margin=ft.margin.only(top=20)
            )
        )
        
        self.page.update()
    
    def handle_decision(self, direction: str):
        """Handle a decision choice"""
        if not self.current_decision:
            return
        
        choice = self.current_decision.get(direction, {})
        effects = choice.get("effects", {})
        next_id = choice.get("next", None)
        
        # Apply resource effects
        for resource_id, change in effects.items():
            if resource_id in self.resource_values:
                resource_info = self.resources.get(resource_id, {})
                min_val = resource_info.get("min", 0)
                max_val = resource_info.get("max", 100)
                
                # Apply change with constraints
                old_value = self.resource_values[resource_id]
                new_value = old_value + change
                new_value = max(min_val, min(max_val, new_value))
                self.resource_values[resource_id] = new_value
        
        # Update the resource display
        self.update_resource_display()
        
        # Check for game over
        game_over = self._check_game_over()
        
        # Show feedback
        if game_over:
            self._show_game_over()
        elif next_id:
            # To show a confirmation between decisions, uncomment this section
            # and comment out the immediate show_decision call
            """
            confirmation_card = ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(f"You chose: {choice.get('text', '')}", size=16, weight="bold"),
                            ft.ElevatedButton(
                                text="Continue →",
                                on_click=lambda _: self.show_decision(next_id),
                                bgcolor="#2196f3",
                                color="white"
                            )
                        ],
                        spacing=10,
                        horizontal_alignment="center"
                    ),
                    padding=20
                ),
                width=350,
                elevation=5
            )
            
            # Replace the decision card
            if len(self.page.controls) > 3:
                self.page.controls.pop()
            
            self.page.add(
                ft.Container(
                    content=confirmation_card,
                    alignment="center",
                    margin=ft.margin.only(top=20)
                )
            )
            
            self.page.update()
            """
            
            # Direct transition to next decision
            self.show_decision(next_id)
    
    def _check_game_over(self):
        """Check if the game is over based on resource values"""
        for resource_id, value in self.resource_values.items():
            resource_info = self.resources.get(resource_id, {})
            min_val = resource_info.get("min", 0)
            
            # Check if it's a critical resource (these are just examples)
            is_critical = resource_id in ["money", "fuel", "oxygen", "food"]
            
            if is_critical and value <= min_val:
                return True
        
        return False
    
    def _show_game_over(self):
        """Show game over screen"""
        if len(self.page.controls) > 3:
            self.page.controls.pop()  # Remove decision card
        
        game_over_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Game Over", size=30, weight="bold", color="#f44336"),
                        ft.Text("Your journey has come to an end.", size=16),
                        ft.Row(
                            controls=[
                                ft.ElevatedButton(
                                    text="Play Again",
                                    on_click=lambda _: self.show_decision("start"),
                                    bgcolor="#2196f3",
                                    color="white"
                                ),
                                ft.ElevatedButton(
                                    text="Main Menu",
                                    on_click=lambda _: self.show_game_selection(),
                                    bgcolor="#9e9e9e",
                                    color="white"
                                )
                            ],
                            alignment="center",
                            spacing=10
                        )
                    ],
                    horizontal_alignment="center",
                    spacing=20
                ),
                padding=30
            ),
            width=350,
            elevation=5
        )
        
        self.page.add(
            ft.Container(
                content=game_over_card,
                alignment="center",
                margin=ft.margin.only(top=20)
            )
        )
        
        self.page.update()
    
    def show_error(self, message: str):
        """Show an error message"""
        self.page.controls.clear()
        
        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text("SwipeFate", size=24, weight="bold", color="white"),
                    ft.IconButton(
                        icon=ft.icons.HOME,
                        icon_color="white",
                        on_click=lambda _: self.show_game_selection()
                    )
                ],
                alignment="spaceBetween"
            ),
            bgcolor="#2196f3",
            padding=15
        )
        
        self.page.add(
            header,
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.icons.ERROR_OUTLINE, size=64, color="#f44336"),
                        ft.Text("Error", size=28, weight="bold", color="#f44336"),
                        ft.Text(message, size=16, text_align="center"),
                        ft.ElevatedButton(
                            text="Back to Menu",
                            on_click=lambda _: self.show_game_selection()
                        )
                    ],
                    alignment="center",
                    horizontal_alignment="center",
                    spacing=20
                ),
                padding=30,
                alignment="center"
            )
        )
        
        self.page.update()

def main(page: ft.Page):
    """Main entry point for the application"""
    # Use the simple UI which is compatible with all Flet versions
    SimpleGameUI(page)

if __name__ == "__main__":
    ft.app(target=main)