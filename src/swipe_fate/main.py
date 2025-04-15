import flet as ft
import json

def main(page: ft.Page):
    """Main entry point for the application"""
    print("Starting basic SwipeFate")
    
    # Configure default page settings
    page.title = "SwipeFate"
    page.bgcolor = "white"
    page.padding = 20
    
    # Add a header
    header = ft.Text(value="SwipeFate", size=30, color="white", bgcolor="blue", width=600)
    page.add(header)
    
    # Create a container for content
    content_area = ft.Container(
        content=None,
        padding=20,
        width=600,
        bgcolor="#f0f0f0",
        border_radius=10
    )
    page.add(content_area)
    
    # Create a back button (initially hidden)
    back_button = ft.ElevatedButton(
        text="← Back to Game Selection",
        on_click=lambda _: show_game_selection(),
        visible=False
    )
    page.add(back_button)
    
    # Show game selection
    def show_game_selection():
        print("Showing game selection")
        
        back_button.visible = False
        
        selection_text = ft.Text(value="Choose a game:", size=20)
        
        button1 = ft.ElevatedButton(
            text="Business Simulator", 
            on_click=lambda _: load_game("configs/business.json"),
            bgcolor="blue", 
            color="white",
            width=200
        )
        
        button2 = ft.ElevatedButton(
            text="Space Explorer", 
            on_click=lambda _: load_game("configs/space_exploration.json"),
            bgcolor="purple", 
            color="white",
            width=200
        )
        
        content_area.content = ft.Column(
            controls=[selection_text, button1, button2],
            spacing=20,
            alignment="center"
        )
        page.update()
    
    # Game state variables
    decisions = []
    current_resources = {}
    
    # Load game config
    def load_game(config_file):
        print(f"Loading game: {config_file}")
        nonlocal decisions, current_resources
        
        # Show loading indicator
        content_area.content = ft.Text(value="Loading game...", size=20)
        page.update()
        
        try:
            # Read JSON file
            with open(config_file, "r") as f:
                file_content = f.read()
            
            # Pre-process to handle + and - signs
            import re
            clean_content = re.sub(r'(\s+)"(\w+)":\s*\+(\d+)', r'\1"\2": \3', file_content)
            
            # Parse the JSON
            game_data = json.loads(clean_content)
            
            # Extract game info
            game_name = game_data.get("metadata", {}).get("name", "Game")
            decisions = game_data.get("decisions", [])
            current_resources = game_data.get("resources", {})
            
            print(f"Loaded {game_name} with {len(decisions)} decisions")
            
            # Make back button visible
            back_button.visible = True
            
            # Start the game with first decision
            if decisions:
                show_decision(decisions[0], resources)
            else:
                content_area.content = ft.Text(value="No decisions found in game data", size=20, color="red")
                page.update()
                
        except Exception as e:
            content_area.content = ft.Text(value=f"Error loading game: {str(e)}", size=20, color="red")
            page.update()
            print(f"Error loading game: {e}")
    
    # Show a decision card
    def show_decision(decision, resources):
        print(f"Showing decision: {decision.get('id')}")
        
        decision_text = decision.get("text", "Decision text missing")
        left_option = decision.get("left", {}).get("text", "Left option")
        right_option = decision.get("right", {}).get("text", "Right option")
        
        # Create resource display
        resource_items = []
        for resource_id, resource_info in resources.items():
            resource_value = resource_info.get("initial", 0)
            display_name = resource_info.get("display_name", resource_id.title())
            
            resource_row = ft.Text(
                value=f"{display_name}: {resource_value}",
                size=16
            )
            resource_items.append(resource_row)
        
        resources_section = ft.Column(
            controls=[ft.Text(value="Resources:", size=18, weight="bold")] + resource_items,
            spacing=5
        )
        
        # Create decision card
        decision_card = ft.Container(
            content=ft.Column([
                ft.Text(value=decision_text, size=20, weight="bold"),
                ft.Divider(),
                ft.Text(value="Options:", size=16),
                ft.Row([
                    ft.ElevatedButton(
                        text=left_option,
                        bgcolor="red",
                        color="white",
                        on_click=lambda _: handle_choice(decision, "left", resources)
                    ),
                    ft.ElevatedButton(
                        text=right_option,
                        bgcolor="green",
                        color="white",
                        on_click=lambda _: handle_choice(decision, "right", resources)
                    )
                ], alignment="spaceAround")
            ]),
            padding=20,
            bgcolor="white",
            border=ft.border.all(1, "blue"),
            border_radius=10
        )
        
        # Combine everything
        content_area.content = ft.Column([
            resources_section,
            ft.Container(height=20),  # Spacer
            decision_card
        ])
        page.update()
    
    # Handle a decision choice
    def handle_choice(decision, direction, resources):
        print(f"Choice made: {direction}")
        nonlocal current_resources
        
        choice = decision.get(direction, {})
        effects = choice.get("effects", {})
        next_id = choice.get("next", None)
        
        # Apply effects to resources
        for resource_id, change in effects.items():
            if resource_id in current_resources:
                resource_config = current_resources[resource_id]
                
                # Update the initial value (which we use as current value)
                current_value = resource_config.get("initial", 0)
                new_value = current_value + change
                
                # Apply min/max constraints
                min_val = resource_config.get("min", 0)
                max_val = resource_config.get("max", 1000)
                new_value = max(min_val, min(max_val, new_value))
                
                # Update the resource
                resource_config["initial"] = new_value
                print(f"Updated {resource_id}: {current_value} → {new_value}")
        
        # Show feedback
        content_area.content = ft.Text(
            value=f"You chose: {choice.get('text', direction)}",
            size=20,
            color="blue"
        )
        page.update()
        
        # Find next decision
        next_decision = None
        if next_id:
            for d in range(len(decisions)):
                if decisions[d].get("id") == next_id:
                    next_decision = decisions[d]
                    break
        
        # Show next decision after delay
        if next_decision:
            def show_next():
                show_decision(next_decision, current_resources)
            
            page.after(1000, show_next)
    
    # Start with game selection
    show_game_selection()
    print("Initial setup complete")

if __name__ == "__main__":
    ft.app(target=main)