"""Main application controller for SwipeVerse."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import flet as ft
from flet import Page

# Global settings/state (consider moving to a dedicated state management class later)
APP_CONFIG: Dict[str, Any] = {
    "game_theme": "tutorial",
    "debug": False,
    "assets_dir": "swipe_verse/assets",  # Relative path for Flet
    "scenarios_dir": "swipe_verse/scenarios", # Relative path
    "version": "0.1.11", # Consider fetching from pyproject.toml
    "platform": "desktop" # Default, Flet might override
}
GAME_DATA: Dict[str, Any] = {}
GAME_STATE: Dict[str, Any] = {}


def load_game_data(game_theme: str) -> Dict[str, Any]:
    """Load game data from JSON file based on theme."""
    global APP_CONFIG
    game_file = f"{game_theme}_game.json"
    # Construct path relative to project root
    scenarios_base = Path(__file__).resolve().parent.parent 
    game_path = scenarios_base / APP_CONFIG["scenarios_dir"] / game_file

    # Use this when running as installed package (adjust if needed)
    # fallback_path = Path(__file__).parent / "scenarios" / game_file
    
    print(f"Attempting to load game data from: {game_path}")
    if not game_path.exists():
        print(f"Error: Game file not found at {game_path}")
        # print(f"Attempting fallback: {fallback_path}")
        # if fallback_path.exists():
        #     game_path = fallback_path
        # else:
        #     print(f"Error: Fallback game file also not found at {fallback_path}")
        #     return {"error": "Game data not found"}
        return {"error": "Game data not found"}
        
    try:
        with open(game_path, "r", encoding="utf-8") as f:
            data: Dict[str, Any] = json.load(f)
            print(f"Successfully loaded game: {data.get('game_info',{}).get('title')}")
            return data
    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
        print(f"Error loading game data from {game_path}: {e}")
        # Return a minimal structure on error
        return {
            "game_info": {"title": "Error Loading Game", "description": "Could not load game data."},
            "theme": {"name": "Default Theme", "resource_icons": {}},
            "game_settings": {"initial_resources": {}},
            "cards": []
        }

def initialize_game_state(game_data: Dict[str, Any]) -> Dict[str, Any]:
    """Initialize the game state based on loaded game data."""
    return {
        "current_card_id": None,
        "resources": game_data.get("game_settings", {}).get("initial_resources", {}).copy(),
        "cards": {card["id"]: card for card in game_data.get("cards", [])},
        "history": []
    }

# Helper function to get card by ID
def get_card(card_id: str) -> Optional[Dict[str, Any]]:
    global GAME_STATE
    card: Optional[Dict[str, Any]] = GAME_STATE.get("cards", {}).get(card_id)
    return card

# Helper function to handle card choice
def handle_card_choice(card_id: str, choice_direction: str) -> Optional[str]:
    global GAME_STATE
    card = get_card(card_id)
    if not card:
        return None
    
    choice = card.get("choices", {}).get(choice_direction)
    if not choice:
        return None
    
    # Apply resource effects
    effects = choice.get("effects", {})
    for resource, value in effects.items():
        if resource in GAME_STATE.get("resources", {}):
            GAME_STATE["resources"][resource] += value
    
    # Record in history
    GAME_STATE.setdefault("history", []).append({
        "card_id": card_id,
        "choice": choice_direction,
        "effects": effects
    })
    
    # Get next card
    next_card_id: Optional[str] = choice.get("next_card")
    if next_card_id:
        GAME_STATE["current_card_id"] = next_card_id
        return next_card_id
    
    GAME_STATE["current_card_id"] = None # Explicitly set to None if no next card
    return None

def main(page: Page) -> None:
    """Initialize the Flet app on the page."""
    global APP_CONFIG, GAME_DATA, GAME_STATE
    
    # --- Initialization --- 
    print("Starting main Flet function...")
    APP_CONFIG["platform"] = page.platform # Get actual platform
    APP_CONFIG["version"] = page.app_version if hasattr(page, 'app_version') else APP_CONFIG["version"] # Get version if available
    
    # Load initial game data
    GAME_DATA = load_game_data(APP_CONFIG["game_theme"])
    GAME_STATE = initialize_game_state(GAME_DATA)
    
    # If game data failed to load, show error message
    if GAME_DATA.get("error"):
        page.add(ft.Text(f"Error: {GAME_DATA.get('error')}", color=ft.colors.RED))
        page.update()
        return
        
    print(f"Initial game state loaded for theme: {APP_CONFIG['game_theme']}")
    print(f"Initial resources: {GAME_STATE.get('resources')}")
    
    # --- Page Configuration --- 
    page.title = f"SwipeVerse {APP_CONFIG.get('version', '')}"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK
    # page.vertical_alignment = ft.MainAxisAlignment.CENTER
    # page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    # Configure page size based on platform
    if page.platform in ["android", "ios"]:
        page.window_width = 400
        page.window_height = 800
        page.window_resizable = False
        page.window_maximizable = False
    else:
        page.window_width = 500 # Adjusted for better card fit
        page.window_height = 750
        page.window_resizable = True
        page.window_maximizable = True
    
    # --- State Variables --- 
    # Using page.client_storage for simple state persistence across reloads (web)
    current_screen = page.client_storage.get("current_screen") or "title"
    # Ensure game state uses client storage if available (optional)
    if page.client_storage.contains_key("game_state"): 
        loaded_state = page.client_storage.get("game_state")
        if isinstance(loaded_state, dict):
            GAME_STATE = loaded_state # Restore game state
            print("Restored game state from client storage")
        else:
             print("Invalid game state in client storage, resetting.")
             page.client_storage.remove("game_state") # Clear invalid state
             GAME_STATE = initialize_game_state(GAME_DATA) # Re-initialize
    
    # --- UI Elements --- 
    # Main container that will hold all screens
    main_container = ft.Container(
        expand=True,
        content=None,
        alignment=ft.alignment.center,
    )
    
    # Resource Indicators (will be updated dynamically)
    resource_indicators_row = ft.Row(
        controls=[], # Populated in show_game_screen
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10,
    )

    # Card Display Area (will be updated dynamically)
    card_display_area = ft.Column( # Use Column for centering card + actions
        controls=[], # Populated in show_game_screen
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.CENTER,
        expand=True, # Make it take available vertical space
    )
    
    # Header Container (reused across screens)
    header_container = ft.Container(
        content=None, # Set dynamically
        padding=10,
        bgcolor=ft.colors.SURFACE_VARIANT,
        # width=page.window_width, # Let it expand naturally
    )
    
    # --- Screen Building Functions --- 

    def update_resource_indicators():
        """Rebuilds the resource indicators row based on current GAME_STATE."""
        global GAME_DATA, GAME_STATE
        resource_icons = GAME_DATA.get("theme", {}).get("resource_icons", {})
        indicators = []
        for name, value in GAME_STATE.get("resources", {}).items():
            icon_rel_path = resource_icons.get(name, '')
            # Flet assets paths are relative to the `assets_dir` passed to ft.app
            # Remove the initial `swipe_verse/assets/` part
            flet_icon_src = icon_rel_path.removeprefix('swipe_verse/assets/').lstrip('/') if icon_rel_path else ''
            
            indicators.append(
                ft.Container(
                    content=ft.Stack([
                        ft.Image(
                            src=flet_icon_src,
                            width=40,
                            height=40,
                            fit=ft.ImageFit.CONTAIN,
                            error_content=ft.Icon(ft.icons.BROKEN_IMAGE_OUTLINED, size=30),
                        ),
                        ft.Container( # Fill overlay
                            width=40,
                            height=40 * (1 - min(max(value, 0), 100) / 100),
                            bgcolor=ft.colors.with_opacity(0.6, ft.colors.BLACK),
                            alignment=ft.alignment.top_center,
                        )
                    ]),
                    width=50,
                    height=50,
                    tooltip=f"{name.capitalize()}: {value}",
                    margin=3,
                )
            )
        resource_indicators_row.controls = indicators
        # No page.update() here, called by the screen function

    def navigate_to(screen_name):
        """Handles navigation between screens."""
        nonlocal current_screen
        current_screen = screen_name
        page.client_storage.set("current_screen", screen_name) # Persist screen
        
        # Clear main container before loading new screen
        main_container.content = None 
        page.clean() # Ensure previous screen's controls are removed
        
        if screen_name == "title":
            show_title_screen()
        elif screen_name == "game":
            show_game_screen()
        elif screen_name == "settings":
            show_settings_screen()
        elif screen_name == "achievements":
            show_achievements_screen()
        else:
            show_title_screen() # Default to title
            
        page.update()
        print(f"Navigated to: {screen_name}")
        
    def show_title_screen():
        """Builds and displays the title screen."""
        title_content = ft.Column(
            controls=[
                ft.Text("SwipeVerse", size=40, weight=ft.FontWeight.BOLD),
                ft.Text("A card-based decision game", size=20),
                ft.Container(height=20), 
                ft.ElevatedButton("Start Game", width=200, on_click=lambda e: navigate_to("game")),
                ft.ElevatedButton("Settings", width=200, on_click=lambda e: navigate_to("settings")),
                ft.ElevatedButton("Achievements", width=200, on_click=lambda e: navigate_to("achievements")),
                ft.Container(height=10),
                ft.Text(f"Version {APP_CONFIG.get('version', '')}", size=12, italic=True, color=ft.colors.GREY_500),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
            expand=True,
        )
        main_container.content = title_content
        # No page.update() here, called by navigate_to

    def show_game_screen():
        """Builds and displays the main game screen."""
        global GAME_STATE, GAME_DATA
        
        # If no current card, try to start with the first card
        if not GAME_STATE.get("current_card_id") and GAME_DATA.get("cards"):
            first_card_id = GAME_DATA["cards"][0]["id"]
            GAME_STATE["current_card_id"] = first_card_id
            print(f"Starting game with first card: {first_card_id}")
        
        current_card = get_card(GAME_STATE.get("current_card_id", ""))
        
        # --- Card Display Logic --- 
        card_controls = []
        if not current_card:
            # No card or end of game
            card_controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("Game Over" if GAME_STATE.get("history") else "No cards available", size=24, weight=ft.FontWeight.BOLD),
                        ft.Text("Thanks for playing!" if GAME_STATE.get("history") else "Check game configuration."),
                        ft.Container(height=20),
                        ft.ElevatedButton("Back to Menu", on_click=lambda e: navigate_to("title")),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=20,
                    border_radius=10,
                    width=300,
                    alignment=ft.alignment.center,
                )
            )
        else:
            # Build the card display with swipe interaction
            card_image_path = current_card.get("image", "")
            # Flet expects paths relative to the `assets_dir`
            relative_card_image_path = card_image_path.removeprefix('swipe_verse/assets/').lstrip('/') if card_image_path else ""
            
            # Card visual content
            card_inner_content = ft.Column([
                ft.Text(current_card.get("title", ""), size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Container(
                    content=ft.Image(
                        src=relative_card_image_path,
                        # width=250, # Let container define size
                        height=150,
                        fit=ft.ImageFit.CONTAIN,
                        error_content=ft.Container( # Placeholder if image missing
                            height=150, 
                            alignment=ft.alignment.center, 
                            content=ft.Icon(ft.icons.IMAGE_NOT_SUPPORTED_OUTLINED, color=ft.colors.GREY_500, size=40)
                        ),
                        border_radius=ft.border_radius.all(8),
                    ), 
                    padding=ft.padding.symmetric(vertical=10)
                ) if card_image_path else ft.Container(height=10), # Space if no image
                ft.Text(current_card.get("text", ""), size=16, text_align=ft.TextAlign.CENTER, selectable=True),
            ], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            
            card_inner_container = ft.Container(
                content=card_inner_content,
                padding=15,
                bgcolor=ft.colors.SURFACE_VARIANT,
                border_radius=10,
                width=300,
                # height=400, # Dynamic height based on content
                alignment=ft.alignment.center,
                border=ft.border.all(1, ft.colors.with_opacity(0.1, ft.colors.WHITE)),
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=5,
                    color=ft.colors.with_opacity(0.1, ft.colors.BLACK),
                    offset=ft.Offset(2, 2),
                )
            )

            # Draggable container for swipe effect
            drag_container = ft.Container(
                content=card_inner_container,
                width=320, # Slightly wider for effect visibility
                # height=450, # Let content define height
                alignment=ft.alignment.center,
                animate_offset=ft.animation.Animation(200, ft.AnimationCurve.EASE_OUT),
                animate_rotation=ft.animation.Animation(200, ft.AnimationCurve.EASE_OUT),
                animate_opacity=ft.animation.Animation(200, ft.AnimationCurve.EASE_OUT),
            )

            # Swipe state variables (need to be local to the instance of the card)
            swipe_state = {"distance": 0}
            swipe_threshold = 80  # Distance required for a decision
            max_swipe_angle = 8   # Maximum rotation angle in degrees
            max_offset = 120      # Maximum offset for card movement
            
            # Drag handlers need to access and modify swipe_state
            def handle_drag_update(e: ft.DragUpdateEvent):
                state = swipe_state # Capture local state
                state["distance"] += e.delta_x
                
                # Clamp distance for calculations
                clamped_distance = min(max(state["distance"], -max_offset*1.5), max_offset*1.5)
                normalized_distance = min(abs(clamped_distance) / swipe_threshold, 1)
                
                rotation_rad = (clamped_distance / max_offset) * (max_swipe_angle * (3.14159 / 180))
                offset_x = clamped_distance / drag_container.width if drag_container.width else 0
                
                drag_container.offset = ft.transform.Offset(offset_x, 0)
                drag_container.rotate = ft.transform.Rotate(angle=rotation_rad, alignment=ft.alignment.center)
                
                # Visual feedback (opacity change on the container)
                opacity_multiplier = 1.0 - (normalized_distance * 0.3) # Fade slightly
                drag_container.opacity = opacity_multiplier
                
                # Choice text visibility (Optional)
                # Could add Text controls here and adjust their visibility/opacity

                page.update()

            def handle_drag_end(e: ft.DragEndEvent):
                state = swipe_state # Capture local state
                final_distance = state["distance"]
                state["distance"] = 0 # Reset for next interaction

                if abs(final_distance) > swipe_threshold:
                    direction = "right" if final_distance > 0 else "left"
                    final_offset_x = 1.5 if direction == "right" else -1.5 
                    final_rotation = max_swipe_angle if direction == "right" else -max_swipe_angle
                    final_rotation_rad = final_rotation * (3.14159 / 180)
                    
                    # Animate card off-screen
                    drag_container.offset = ft.transform.Offset(final_offset_x, 0)
                    drag_container.rotate = ft.transform.Rotate(angle=final_rotation_rad, alignment=ft.alignment.center)
                    drag_container.opacity = 0 # Fade out
                    page.update() 
                    
                    # Process the choice after animation (Flet doesn't block, so this happens quickly)
                    # Consider ft.Timer for a delay if needed
                    process_choice(direction)
                    
                else:
                    # Reset card position animation
                    drag_container.offset = ft.transform.Offset(0, 0)
                    drag_container.rotate = ft.transform.Rotate(0)
                    drag_container.opacity = 1.0
                    page.update()
            
            # Gesture detector wraps the draggable container
            card_gesture_detector = ft.GestureDetector(
                mouse_cursor=ft.MouseCursor.MOVE,
                drag_interval=10, # Milliseconds between drag updates
                on_horizontal_drag_update=handle_drag_update,
                on_horizontal_drag_end=handle_drag_end,
                content=drag_container,
                # Set hit testing behavior if needed
                # hit_test_behavior=ft.HitTestBehavior.OPAQUE,
            )
            
            card_controls.append(card_gesture_detector)

            # Choice Buttons (below the card)
            left_choice_data = current_card.get("choices", {}).get("left", {})
            right_choice_data = current_card.get("choices", {}).get("right", {})
            card_controls.append(
                ft.Row([
                        ft.Text(left_choice_data.get("text", "..."), italic=True, color=ft.colors.GREY_500),
                        ft.Container(width=40, expand=True), # Spacer
                        ft.Text(right_choice_data.get("text", "..."), italic=True, color=ft.colors.GREY_500),
                    ],
                    width=300,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    # visible=False # Initially hidden, shown on hover/drag?
                )
            )
        
        # --- Process Choice Function --- 
        def process_choice(direction):
            global GAME_STATE, GAME_DATA
            
            current_card_id = GAME_STATE.get("current_card_id")
            if not current_card_id:
                 print("Error: process_choice called with no current card ID")
                 return
                 
            print(f"Processing choice '{direction}' for card {current_card_id}")
            next_card_id = handle_card_choice(current_card_id, direction)
            page.client_storage.set("game_state", GAME_STATE) # Save state
            
            # Show effects feedback (Snackbar)
            card = get_card(current_card_id) # Get the card again (it might be None now)
            choice_data = card.get("choices", {}).get(direction, {}) if card else {}
            effects = choice_data.get("effects", {})
            effect_text = ", ".join([f"{k.capitalize()}: {v:+d}" for k, v in effects.items()]) if effects else "No effect"
            
            page.show_snack_bar(ft.SnackBar(
                content=ft.Text(f"{choice_data.get('text', direction.capitalize())}. {effect_text}"),
                # action="OK",
                duration=2500 # milliseconds
            ))
            
            # Update UI - refresh the game screen for the next card or game over state
            show_game_screen() # This will rebuild the card area etc.
            page.update() 
            
        # --- Assemble Game Screen --- 
        # Header
        header_container.content = ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK, tooltip="Back to Menu", on_click=lambda e: navigate_to("title")),
                ft.Text(GAME_DATA.get("game_info", {}).get("title", "Game"), size=20, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),
                ft.Container(width=40) # Balance the back button space
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        update_resource_indicators() # Update the indicator row
        card_display_area.controls = card_controls # Set card content

        # Combine elements for the game screen view
        main_container.content = ft.Column([
            header_container,
            resource_indicators_row,
            # ft.Divider(height=1, color=ft.colors.with_opacity(0.2, ft.colors.WHITE)),
            ft.Container(height=10),
            card_display_area, # This column now expands and centers
            ft.Container(height=20), # Bottom padding
        ], expand=True, spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        # No page.update() here, called by navigate_to

    def show_settings_screen():
        """Builds and displays the settings screen."""
        global APP_CONFIG, GAME_DATA, GAME_STATE
        
        # Header
        header_container.content = ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK, tooltip="Back to Menu", on_click=lambda e: navigate_to("title")),
                ft.Text("Settings", size=20, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),
                 ft.Container(width=40) # Balance the back button space
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # Settings Controls
        game_theme_dropdown = ft.Dropdown(
            label="Game Scenario",
            options=[
                ft.dropdown.Option("tutorial", "Tutorial"),
                ft.dropdown.Option("kingdom", "Medieval Kingdom"),
                ft.dropdown.Option("business", "Corporate Business"),
                # Add more dynamically later?
            ],
            value=APP_CONFIG.get("game_theme", "tutorial"),
            width=300,
        )

        # Add more settings controls here (visuals, difficulty etc.)

        def apply_settings(e):
            global APP_CONFIG, GAME_DATA, GAME_STATE
            new_theme = game_theme_dropdown.value
            if new_theme != APP_CONFIG.get("game_theme"):
                print(f"Changing theme to: {new_theme}")
                APP_CONFIG["game_theme"] = new_theme
                page.client_storage.remove("game_state") # Clear old game state
                # Reload data and reset state
                GAME_DATA = load_game_data(new_theme)
                GAME_STATE = initialize_game_state(GAME_DATA)
                print("Reloaded game data and reset state for new theme.")
                
                # Add feedback
                page.show_snack_bar(ft.SnackBar(ft.Text(f"Switched to {new_theme.capitalize()} scenario."), duration=2000))
            else:
                 page.show_snack_bar(ft.SnackBar(ft.Text("Settings applied."), duration=1500))
                 
            # Navigate back to title after applying
            navigate_to("title")

        settings_content = ft.Column([
            ft.Text("Game Options", size=18, weight=ft.FontWeight.BOLD),
            game_theme_dropdown,
            # Add other settings here
            ft.Container(height=20),
            ft.ElevatedButton("Apply & Back to Menu", width=300, on_click=apply_settings),
            ft.Container(height=20),
            ft.Text("More settings coming soon!", italic=True, color=ft.colors.GREY_500)
        ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True, alignment=ft.MainAxisAlignment.CENTER)
        
        # Combine header and content
        main_container.content = ft.Column([
            header_container,
            ft.Container(content=settings_content, expand=True, alignment=ft.alignment.center, padding=20)
        ], spacing=0, expand=True)
        # No page.update() here, called by navigate_to

    def show_achievements_screen():
        """Builds and displays the achievements screen."""
        # Header
        header_container.content = ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK, tooltip="Back to Menu", on_click=lambda e: navigate_to("title")),
                ft.Text("Achievements", size=20, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),
                 ft.Container(width=40) # Balance the back button space
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            
        achievements_content = ft.Column([
            ft.Icon(ft.icons.EMOJI_EVENTS_OUTLINED, size=50, color=ft.colors.AMBER),
            ft.Text("Achievements", size=24, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=ft.Text("No achievements unlocked yet. Keep playing!", text_align=ft.TextAlign.CENTER),
                padding=20,
                # bgcolor=ft.colors.SURFACE_VARIANT,
                border_radius=10,
                width=300,
                alignment=ft.alignment.center,
            ),
        ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True, alignment=ft.MainAxisAlignment.CENTER)

        # Combine header and content
        main_container.content = ft.Column([
            header_container,
            ft.Container(content=achievements_content, expand=True, alignment=ft.alignment.center, padding=20)
        ], spacing=0, expand=True)
        # No page.update() here, called by navigate_to
        
    # --- Initial Setup --- 
    page.add(main_container) # Add the main container to the page
    navigate_to(current_screen) # Load the initial screen (either default or from storage)
    
    print("Flet app initialization complete.")
