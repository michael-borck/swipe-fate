"""Main application controller for SwipeVerse."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import flet as ft
from flet import Page


def initialize_app(
    game_theme: str = "tutorial",
    debug: bool = False,
    assets_dir: Optional[Path] = None,
    version: str = "0.1.11"
) -> Dict[str, Any]:
    """Initialize the application configuration.
    
    Args:
        game_theme: Theme/game to load (tutorial, kingdom, business)
        debug: Enable debug mode
        assets_dir: Custom assets directory path
        version: Application version
        
    Returns:
        Dict containing app configuration
    """
    # Check environment variables for asset paths (used in packaged apps)
    if os.environ.get("SWIPEVERSE_ASSETS"):
        assets_dir = Path(os.environ.get("SWIPEVERSE_ASSETS", ""))
    elif assets_dir is None:
        assets_dir = Path(__file__).parent / "assets"
    
    # Ensure assets_dir exists
    if not assets_dir.exists():
        print(f"Warning: Assets directory {assets_dir} does not exist. Using package resources.")
        # Fall back to a path that will be resolved by Flet for package resources
        assets_dir = Path(".")
    
    scenarios_dir = os.environ.get("SWIPEVERSE_SCENARIOS")
    if not scenarios_dir:
        scenarios_dir = str(Path(__file__).parent / "scenarios")
    
    # Ensure scenarios_dir exists
    if not Path(scenarios_dir).exists():
        print(f"Warning: Scenarios directory {scenarios_dir} does not exist.")
        # Try to use a relative path that will be resolved properly in packaged app
        alt_scenarios_dir = str(Path(__file__).parent / "scenarios")
        if Path(alt_scenarios_dir).exists():
            scenarios_dir = alt_scenarios_dir
            print(f"Using alternative scenarios directory: {scenarios_dir}")
    
    # Print debugging information if in debug mode
    if debug:
        print("[DEBUG] Configuration Information:")
        print(f"[DEBUG] assets_dir: {assets_dir}")
        print(f"[DEBUG] scenarios_dir: {scenarios_dir}")
        print(f"[DEBUG] game_theme: {game_theme}")
        print(f"[DEBUG] version: {version}")
        print(f"[DEBUG] __file__: {__file__}")
        print(f"[DEBUG] Package root: {Path(__file__).parent}")
        
        # Check if directories exist
        print(f"[DEBUG] assets_dir exists: {Path(assets_dir).exists()}")
        print(f"[DEBUG] scenarios_dir exists: {Path(scenarios_dir).exists()}")
        
        # List what's in the assets directory
        try:
            print("[DEBUG] Assets directory contents:")
            for path in Path(assets_dir).glob("**/*"):
                if path.is_file():
                    print(f"[DEBUG]   - {path}")
        except Exception as e:
            print(f"[DEBUG] Error listing assets: {e}")
            
        # Try multiple path formats for a test image
        print("[DEBUG] Testing image path resolution:")
        sample_paths = [
            Path(assets_dir) / "default" / "card_back.png",
            Path(assets_dir) / "default/card_back.png",
            Path(__file__).parent / "assets" / "default" / "card_back.png",
            Path("swipe_verse") / "assets" / "default" / "card_back.png",
            Path("/swipe_verse/assets/default/card_back.png"),
        ]
        
        for path in sample_paths:
            try:
                print(f"[DEBUG]   Path: {path}")
                print(f"[DEBUG]   Exists: {path.exists()}")
            except Exception as e:
                print(f"[DEBUG]   Error checking {path}: {e}")
    
    return {
        "game_theme": game_theme,
        "debug": debug,
        "assets_dir": str(assets_dir),
        "scenarios_dir": scenarios_dir,
        "version": version,
    }


def run_app(
    platform: str = "desktop", 
    config: Optional[Dict[str, Any]] = None,
    port: int = 8550,
    host: str = "127.0.0.1"
) -> None:
    """Run the application on the specified platform.
    
    Args:
        platform: The target platform ("desktop", "web", "android", "ios")
        config: Application configuration
        port: Port to use for web server (web mode only)
        host: Host address to bind to for web server (default: 127.0.0.1)
    """
    if config is None:
        config = initialize_app()
    
    # Store platform in config
    config["platform"] = platform
    
    # Update port and host in config
    if platform == "web":
        config["port"] = port
        config["host"] = host
    
    # Load game data from JSON file
    def load_game_data(game_theme: str) -> Dict[str, Any]:
        """Load game data from JSON file.
        
        Args:
            game_theme: The game theme to load
            
        Returns:
            Game data dictionary
        """
        game_file = f"{game_theme}_game.json"
        config_scenarios_dir = config["scenarios_dir"] if config else ""
        game_path = Path(config_scenarios_dir) / game_file
        
        try:
            with open(game_path, "r", encoding="utf-8") as f:
                game_data: Dict[str, Any] = json.load(f)
                return game_data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading game data: {e}")
            # Return a minimal game data structure if file can't be loaded
            default_data: Dict[str, Any] = {
                "game_info": {
                    "title": "Error Loading Game",
                    "description": "Could not load game data."
                },
                "theme": {
                    "name": "Default Theme"
                },
                "game_settings": {
                    "initial_resources": {}
                },
                "cards": []
            }
            return default_data
    
    # Load the game data based on the selected theme
    game_data = load_game_data(config["game_theme"])
    
    # Initialize game state with typing
    GameState = Dict[str, Any]
    game_state: GameState = {
        "current_card_id": None,
        "resources": game_data.get("game_settings", {}).get("initial_resources", {}),
        "cards": {card["id"]: card for card in game_data.get("cards", [])},
        "history": []
    }
    
    # Helper function to get card by ID
    def get_card(card_id: str) -> Optional[Dict[str, Any]]:
        """Get a card by its ID.
        
        Args:
            card_id: The card ID to look up
            
        Returns:
            Card data dictionary or None if not found
        """
        card: Optional[Dict[str, Any]] = game_state["cards"].get(card_id)
        return card
    
    # Helper function to handle card choice
    def handle_card_choice(card_id: str, choice_direction: str) -> Optional[str]:
        """Handle a card choice.
        
        Args:
            card_id: The current card ID
            choice_direction: 'left' or 'right'
            
        Returns:
            Next card ID or None if no next card is specified
        """
        card = get_card(card_id)
        if not card:
            return None
        
        choice = card.get("choices", {}).get(choice_direction)
        if not choice:
            return None
        
        # Apply resource effects
        effects = choice.get("effects", {})
        for resource, value in effects.items():
            if resource in game_state["resources"]:
                game_state["resources"][resource] += value
        
        # Record in history
        game_state["history"].append({
            "card_id": card_id,
            "choice": choice_direction,
            "effects": effects
        })
        
        # Get next card
        next_card_id: Optional[str] = choice.get("next_card")
        if next_card_id:
            game_state["current_card_id"] = next_card_id
            return next_card_id
        
        return None
    
    def main(page: Page) -> None:
        """Initialize the Flet app on the page."""
        # Configure page based on platform
        if platform == "android" or platform == "ios":
            # Mobile configuration
            page.window_width = 400
            page.window_height = 800
            page.window_resizable = False
            page.window_maximizable = False
        else:
            # Desktop/Web configuration
            page.window_width = 800
            page.window_height = 600
            page.window_resizable = True
            page.window_maximizable = True
        
        # Set app title with version
        version = config.get('version', '') if config else ''
        page.title = f"SwipeVerse {version}"
        page.padding = 0
        page.theme_mode = ft.ThemeMode.DARK
        
        # Track current screen for navigation
        current_screen = "title"
        
        # Main content container that will hold all screens
        main_container = ft.Container(
            expand=True,
            content=None,
        )
        
        # Function to navigate to different screens
        def navigate_to(screen_name):
            nonlocal current_screen
            current_screen = screen_name
            
            if screen_name == "title":
                show_title_screen()
            elif screen_name == "game":
                show_game_screen()
            elif screen_name == "settings":
                show_settings_screen()
            elif screen_name == "achievements":
                show_achievements_screen()
        
        # Title Screen
        def show_title_screen():
            title_content = ft.Column(
                controls=[
                    ft.Text("SwipeVerse", size=40, weight=ft.FontWeight.BOLD),
                    ft.Text("A card-based decision game", size=20),
                    ft.Container(height=20),  # Spacer
                    ft.ElevatedButton(
                        "Start Game",
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                        width=200,
                        on_click=lambda e: navigate_to("game")
                    ),
                    ft.ElevatedButton(
                        "Settings",
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                        width=200,
                        on_click=lambda e: navigate_to("settings")
                    ),
                    ft.ElevatedButton(
                        "Achievements",
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=10),
                        ),
                        width=200,
                        on_click=lambda e: navigate_to("achievements")
                    ),
                    ft.Container(height=10),  # Spacer
                    ft.Text(f"Version {config.get('version', '') if config else ''}", size=12, italic=True),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=12,
            )
            
            main_container.content = title_content
            page.update()
        
        # Game Screen
        def show_game_screen():
            # If no current card, start with the first card
            if not game_state["current_card_id"] and game_data.get("cards"):
                game_state["current_card_id"] = game_data["cards"][0]["id"]
            
            # Get the current card
            current_card = get_card(game_state["current_card_id"]) if game_state["current_card_id"] else None
            
            if not current_card:
                # No card to display, show error
                card_content = ft.Container(
                    content=ft.Column([
                        ft.Text("No cards available", size=24, color=ft.colors.ERROR),
                        ft.Text("Please check your game configuration.", size=16)
                    ]),
                    padding=20,
                    bgcolor=ft.colors.SURFACE_VARIANT,
                    border_radius=10,
                    width=300,
                    height=400,
                    alignment=ft.alignment.center,
                )
                card_actions = ft.Row(
                    controls=[
                        ft.ElevatedButton(
                            "Back to Menu",
                            on_click=lambda e: navigate_to("title")
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            else:
                # Create resource indicators with icons
                # Get resource icons from game data
                resource_icons = game_data.get("theme", {}).get("resource_icons", {})
                
                # Debug resource icons if enabled
                debug_mode = config.get("debug", False) if config else False
                if debug_mode:
                    print(f"Resources: {game_state['resources']}")
                    print(f"Resource icons from game data: {resource_icons}")
                
                # Construct full asset paths from configured assets directory
                assets_dir = config.get("assets_dir", "") if config else ""
                
                # Create resource indicators
                resource_indicators = ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Stack([
                                # Base icon - try different path pattern
                                ft.Image(
                                    # Using /assets/ path pattern for Flet
                                    src=f"/assets/{resource_icons.get(name, '').replace('assets/', '')}" if resource_icons.get(name, '') else "",
                                    width=50,
                                    height=50,
                                    fit=ft.ImageFit.CONTAIN,
                                    error_content=ft.Text(f"Icon not found: {name}"),
                                ),
                                # Colored overlay to indicate level (empty container that is partially filled)
                                ft.Container(
                                    width=50,
                                    height=50 * (1 - value / 100),  # Fill from bottom up
                                    bgcolor=ft.colors.with_opacity(0.5, ft.colors.BLACK),
                                    border_radius=ft.border_radius.only(
                                        top_left=50,
                                        top_right=50,
                                    ),
                                    alignment=ft.alignment.top_center,
                                ),
                                # Resource value text
                                ft.Container(
                                    content=ft.Text(
                                        f"{value}",
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.colors.WHITE,
                                    ),
                                    alignment=ft.alignment.center,
                                )
                            ]),
                            width=60,
                            height=60,
                            tooltip=name.capitalize(),
                            margin=5,
                        )
                        for name, value in game_state["resources"].items()
                        if resource_icons.get(name)  # Only show resources with icons
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                )
                
                # Create the card display
                card_image_path = current_card.get("image", "")
                
                # Construct a path that will work in the installed package
                full_card_image_path = f"/swipe_verse/{card_image_path}" if card_image_path else ""
                
                # Debug image loading
                debug_mode = config.get("debug", False) if config else False
                if debug_mode:
                    print(f"[DEBUG] Card image from JSON: {card_image_path}")
                    print(f"[DEBUG] Full image path used: {full_card_image_path}")
                    assets_dir = config.get("assets_dir", "") if config else ""
                    print(f"[DEBUG] Assets directory setting: {assets_dir}")
                    
                    # Try to check if the image exists at various locations
                    try:
                        direct_path = Path(__file__).parent / card_image_path
                        print(f"[DEBUG] Direct image path: {direct_path}")
                        print(f"[DEBUG] Direct image exists: {direct_path.exists()}")
                    except Exception as e:
                        print(f"[DEBUG] Error checking direct image path: {e}")
                
                # Create the card as a simple container without gestures first
                card_inner = ft.Container(
                    content=ft.Column([
                        ft.Text(current_card.get("title", ""), size=24, weight=ft.FontWeight.BOLD),
                        # Card image - Debug image path directly
                        ft.Container(
                            content=ft.Column([
                                # Show the card image (try multiple path approaches)
                                ft.Image(
                                    src=f"/assets/{card_image_path.replace('assets/', '')}" if card_image_path else "",
                                    width=250,
                                    height=150,
                                    fit=ft.ImageFit.COVER,
                                    error_content=ft.Text(f"Image not found: {card_image_path}"),
                                    border_radius=10,
                                ),
                                # Debug: Display image path for troubleshooting
                                ft.Text(f"Image: /assets/{card_image_path.replace('assets/', '')}", size=10, color=ft.colors.GREY_400),
                            ]) if card_image_path else ft.Container(height=0),
                            padding=10,
                        ),
                        ft.Container(
                            content=ft.Text(current_card.get("text", ""), size=16, text_align=ft.TextAlign.CENTER),
                            padding=10,
                            width=280,
                        ),
                    ]),
                    padding=15,
                    bgcolor=ft.colors.SURFACE_VARIANT,
                    border_radius=10,
                    width=300,
                    height=420,
                    alignment=ft.alignment.center,
                )
                
                # Create a drag area that contains the card
                drag_container = ft.Container(
                    content=card_inner,
                    width=340,
                    height=450,
                    alignment=ft.alignment.center,
                    animate_offset=ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT),
                )
                
                # Add gesture detection to the drag container
                card_detector = ft.GestureDetector(
                    mouse_cursor=ft.MouseCursor.MOVE,
                    on_horizontal_drag_update=lambda e: handle_drag_update(e),
                    on_horizontal_drag_end=lambda e: handle_drag_end(e),
                    content=drag_container
                )
                
                # Swipe variables
                swipe_distance = 0
                swipe_threshold = 100  # Distance required for a decision
                max_swipe_angle = 10  # Maximum rotation angle in degrees
                max_offset = 150  # Maximum offset for card movement
                
                # Drag handlers for card swiping
                def handle_drag_update(e):
                    nonlocal swipe_distance
                    
                    # Get the delta X from the drag event
                    dx = e.delta_x if hasattr(e, 'delta_x') and e.delta_x is not None else 0
                    
                    # Update swipe distance
                    swipe_distance += dx
                    
                    # Calculate normalized values for effects (0-1 range)
                    normalized_distance = min(max(abs(swipe_distance) / swipe_threshold, 0), 1)
                    
                    # Apply rotation and movement based on swipe distance
                    rotation = min(max(swipe_distance / (swipe_threshold / max_swipe_angle), -max_swipe_angle), max_swipe_angle)
                    offset_x = min(max(swipe_distance, -max_offset), max_offset)
                    
                    # Update card position
                    drag_container.offset = ft.transform.Offset(offset_x, 0)
                    drag_container.rotate = ft.transform.Rotate(angle=rotation, alignment=ft.alignment.center)
                    
                    # Visual feedback for swipe direction
                    if swipe_distance > 0:  # Swiping right
                        # Gradually change to green as we approach threshold
                        green_intensity = int(100 + (155 * normalized_distance))
                        card_inner.bgcolor = f"#{green_intensity:02x}ff{green_intensity:02x}80"
                    elif swipe_distance < 0:  # Swiping left
                        # Gradually change to red as we approach threshold
                        red_intensity = int(100 + (155 * normalized_distance))
                        card_inner.bgcolor = f"#ff{red_intensity:02x}{red_intensity:02x}80"
                    else:
                        card_inner.bgcolor = ft.colors.SURFACE_VARIANT
                    
                    # Update UI
                    page.update()
                
                def handle_drag_end(e):
                    nonlocal swipe_distance
                    
                    if abs(swipe_distance) > swipe_threshold:
                        # Direction determined by swipe
                        direction = "right" if swipe_distance > 0 else "left"
                        
                        # Final animation position (off-screen)
                        final_offset = 500 if direction == "right" else -500
                        
                        # Animate card off-screen with proper rotation
                        final_rotation = max_swipe_angle if direction == "right" else -max_swipe_angle
                        drag_container.rotate = ft.transform.Rotate(angle=final_rotation, alignment=ft.alignment.center)
                        drag_container.offset = ft.transform.Offset(final_offset, 0)
                        
                        # Set final color based on direction
                        card_inner.bgcolor = ft.colors.with_opacity(0.8, ft.colors.GREEN_100 if direction == "right" else ft.colors.RED_100)
                        
                        # Update UI to show animation
                        page.update()
                        
                        # Process the choice directly - defer_call isn't available
                        # Use a small delay before processing the choice to let animation be visible
                        page.update()
                        
                        # Process the choice
                        on_card_choice(None, direction)
                    else:
                        # Reset card position with animation
                        drag_container.animate_offset = ft.animation.Animation(300, ft.AnimationCurve.EASE_OUT)
                        drag_container.offset = ft.transform.Offset(0, 0)
                        drag_container.rotate = None
                        card_inner.bgcolor = ft.colors.SURFACE_VARIANT
                        page.update()
                    
                    # Reset swipe distance
                    swipe_distance = 0
                
                # Use the container with gesture detection
                card_content = card_detector
                
                # Create choice buttons with actual choice text
                left_choice = current_card.get("choices", {}).get("left", {})
                right_choice = current_card.get("choices", {}).get("right", {})
                
                # Function to handle card choice
                def on_card_choice(e, direction):
                    # Debug output for card transitions
                    debug_mode = config.get("debug", False) if config else False
                    if debug_mode:
                        print(f"Processing choice: {direction} for card {game_state['current_card_id']}")
                        if current_card:
                            print(f"Current card choices: {current_card.get('choices', {})}")
                    
                    # Handle the choice and get next card ID
                    next_card_id = handle_card_choice(game_state["current_card_id"], direction)
                    
                    if debug_mode:
                        print(f"Next card ID after choice: {next_card_id}")
                        print(f"Updated game state current card: {game_state['current_card_id']}")
                    
                    # Show effects
                    choice = current_card.get("choices", {}).get(direction, {}) if current_card else {}
                    effects = choice.get("effects", {})
                    effect_text = ", ".join([f"{k}: {v:+d}" for k, v in effects.items()])
                    
                    # Show effects in a snack bar
                    page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"{choice.get('text', '')}\nEffects: {effect_text}"),
                        action="OK"
                    )
                    page.snack_bar.open = True
                    page.update()
                    
                    # If there's a next card, refresh the screen to show it
                    if next_card_id:
                        # Force a slight delay before showing the next card
                        # to ensure the animation and snackbar are visible
                        page.update()
                        
                        # Refresh the game screen to show the next card
                        show_game_screen()
                    else:
                        # Check if this is the end of the game or a card without a next_card
                        if not choice.get("next_card"):
                            # End of game, go back to title
                            page.snack_bar = ft.SnackBar(
                                content=ft.Text("End of game! Thanks for playing."),
                                action="OK"
                            )
                            page.snack_bar.open = True
                            page.update()
                            navigate_to("title")
                
                card_actions = ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Column([
                                ft.IconButton(
                                    icon=ft.icons.ARROW_LEFT,
                                    icon_size=30,
                                    tooltip="Swipe Left",
                                    on_click=lambda e: on_card_choice(e, "left")
                                ),
                                ft.Text(
                                    left_choice.get("text", "Swipe Left"), 
                                    size=12,
                                    text_align=ft.TextAlign.CENTER
                                ),
                            ]),
                            padding=5,
                        ),
                        ft.Container(width=50),  # Spacer
                        ft.Container(
                            content=ft.Column([
                                ft.IconButton(
                                    icon=ft.icons.ARROW_RIGHT,
                                    icon_size=30,
                                    tooltip="Swipe Right",
                                    on_click=lambda e: on_card_choice(e, "right")
                                ),
                                ft.Text(
                                    right_choice.get("text", "Swipe Right"), 
                                    size=12,
                                    text_align=ft.TextAlign.CENTER
                                ),
                            ]),
                            padding=5,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            
            # Create header with back button
            header = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.icons.ARROW_BACK,
                            on_click=lambda e: navigate_to("title")
                        ),
                        ft.Text(
                            game_data.get("game_info", {}).get("title", "Game"), 
                            size=20, 
                            weight=ft.FontWeight.BOLD
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                padding=10,
                bgcolor=ft.colors.SURFACE_VARIANT,
                width=page.window_width,
            )
            
            # Combine all game elements
            game_content = ft.Column(
                controls=[
                    resource_indicators if game_state["resources"] else ft.Container(),
                    ft.Container(height=20),  # Spacer
                    card_content,
                    ft.Container(height=10),  # Spacer
                    card_actions,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            )
            
            # Combine header and content
            main_container.content = ft.Column(
                controls=[
                    header,
                    ft.Container(
                        content=game_content,
                        expand=True,
                        alignment=ft.alignment.center,
                    )
                ],
                spacing=0,
                expand=True,
            )
            
            page.update()
        
        # Settings Screen
        def show_settings_screen():
            # Create header with back button
            header = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.icons.ARROW_BACK,
                            on_click=lambda e: navigate_to("title")
                        ),
                        ft.Text("Settings", size=20, weight=ft.FontWeight.BOLD),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                padding=10,
                bgcolor=ft.colors.SURFACE_VARIANT,
                width=page.window_width,
            )
            
            # Settings content
            settings_content = ft.Column(
                controls=[
                    ft.Text("Game Settings", size=24),
                    ft.Dropdown(
                        label="Game",
                        options=[
                            ft.dropdown.Option("tutorial", "Tutorial"),
                            ft.dropdown.Option("kingdom", "Medieval Kingdom"),
                            ft.dropdown.Option("business", "Corporate Business"),
                        ],
                        value=config.get("game_theme") if config else "tutorial",
                        width=300,
                    ),
                    ft.Dropdown(
                        label="Visual Filter",
                        options=[
                            ft.dropdown.Option("none", "None"),
                            ft.dropdown.Option("pixelate", "Pixelate"),
                            ft.dropdown.Option("cartoon", "Cartoon"),
                            ft.dropdown.Option("grayscale", "Grayscale"),
                            ft.dropdown.Option("blur", "Blur"),
                        ],
                        value="none",
                        width=300,
                    ),
                    ft.Dropdown(
                        label="Difficulty",
                        options=[
                            ft.dropdown.Option("easy", "Easy"),
                            ft.dropdown.Option("standard", "Standard"),
                            ft.dropdown.Option("hard", "Hard"),
                        ],
                        value="standard",
                        width=300,
                    ),
                    ft.Container(height=20),  # Spacer
                    ft.ElevatedButton(
                        "Apply Settings",
                        on_click=lambda e: navigate_to("title")
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            )
            
            # Combine header and content
            main_container.content = ft.Column(
                controls=[
                    header,
                    ft.Container(
                        content=settings_content,
                        expand=True,
                        alignment=ft.alignment.center,
                    )
                ],
                spacing=0,
                expand=True,
            )
            
            page.update()
        
        # Achievements Screen
        def show_achievements_screen():
            # Create header with back button
            header = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.IconButton(
                            icon=ft.icons.ARROW_BACK,
                            on_click=lambda e: navigate_to("title")
                        ),
                        ft.Text("Achievements", size=20, weight=ft.FontWeight.BOLD),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                padding=10,
                bgcolor=ft.colors.SURFACE_VARIANT,
                width=page.window_width,
            )
            
            # Achievements content
            achievements_content = ft.Column(
                controls=[
                    ft.Text("Achievements", size=24),
                    ft.Container(
                        content=ft.Text("No achievements yet!"),
                        padding=10,
                        bgcolor=ft.colors.SURFACE_VARIANT,
                        border_radius=10,
                        width=300,
                        alignment=ft.alignment.center,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            )
            
            # Combine header and content
            main_container.content = ft.Column(
                controls=[
                    header,
                    ft.Container(
                        content=achievements_content,
                        expand=True,
                        alignment=ft.alignment.center,
                    )
                ],
                spacing=0,
                expand=True,
            )
            
            page.update()
        
        # Add main container to page
        page.add(main_container)
        
        # Show the title screen by default
        navigate_to("title")
        
        print(f"Page initialized. Controls count: {len(page.controls)}")
    
    if platform == "web":
        # Run as a web application
        # Use the package's assets directory directly
        assets_path = str(Path(__file__).parent / "assets")
        
        # Debug asset path
        if config and config.get("debug", False):
            print(f"Web mode: Using assets_dir: {assets_path}")
            print(f"Assets directory exists: {Path(assets_path).exists()}")
            
        ft.app(
            target=main,
            port=port,
            host=host,
            view=ft.AppView.WEB_BROWSER,
            assets_dir=assets_path
        )
    elif platform == "android":
        # For Android, use a specific configuration
        os.environ["FLET_PLATFORM"] = "android"
        # Use the package's assets directory directly
        assets_path = str(Path(__file__).parent / "assets")
        
        # Debug asset path
        if config and config.get("debug", False):
            print(f"Android mode: Using assets_dir: {assets_path}")
            print(f"Assets directory exists: {Path(assets_path).exists()}")
            
        ft.app(
            target=main,
            assets_dir=assets_path,
            use_color_emoji=True
        )
    elif platform == "ios":
        # For iOS, use a specific configuration
        os.environ["FLET_PLATFORM"] = "ios"
        # Use the package's assets directory directly
        assets_path = str(Path(__file__).parent / "assets")
        
        # Debug asset path
        if config and config.get("debug", False):
            print(f"iOS mode: Using assets_dir: {assets_path}")
            print(f"Assets directory exists: {Path(assets_path).exists()}")
            
        ft.app(
            target=main,
            assets_dir=assets_path,
            use_color_emoji=True
        )
    else:
        # Desktop is the default
        # Use the package's assets directory directly
        assets_path = str(Path(__file__).parent / "assets")
        
        # Debug asset path
        if config and config.get("debug", False):
            print(f"Desktop mode: Using assets_dir: {assets_path}")
            print(f"Assets directory exists: {Path(assets_path).exists()}")
            
        ft.app(
            target=main,
            assets_dir=assets_path
        )