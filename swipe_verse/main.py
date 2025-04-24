"""Main application controller for SwipeVerse."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import flet as ft
from flet import Page

# Global settings/state (Restored)
APP_CONFIG: Dict[str, Any] = {
    "game_theme": "tutorial",
    "debug": False,
    "assets_dir": "swipe_verse/assets", # <--- Crucial for ft.app
    "scenarios_dir": "swipe_verse/scenarios",
    "version": "0.1.11",
    "platform": "desktop"
}
GAME_DATA: Dict[str, Any] = {}
GAME_STATE: Dict[str, Any] = {}

# Function definitions (Restored)
def load_game_data(game_theme: str) -> Dict[str, Any]:
    """Load game data from JSON file based on theme."""
    global APP_CONFIG
    game_file = f"{game_theme}_game.json"
    scenarios_base = Path(__file__).resolve().parent.parent 
    game_path = scenarios_base / APP_CONFIG.get("scenarios_dir", "swipe_verse/scenarios") / game_file
    print(f"--- Attempting to load game data from: {game_path} ---")
    if not game_path.exists():
        print(f"### Error: Game file not found at {game_path} ###")
        return {"error": "Game data not found", "game_info": {"title": "Error"}, "theme": {}, "game_settings": {}, "cards": []}
    try:
        with open(game_path, "r", encoding="utf-8") as f:
            data: Dict[str, Any] = json.load(f)
            print(f"--- Successfully loaded game: {data.get('game_info', {}).get('title')} ---")
            # *** NO Path Adjustment - Use paths AS-IS from JSON ***
            return data
    except Exception as e:
        print(f"### Error loading game data from {game_path}: {e} ###")
        return {"error": f"Error loading data: {e}", "game_info": {"title": "Error"}, "theme": {}, "game_settings": {}, "cards": []}

def initialize_game_state(game_data: Dict[str, Any]) -> Dict[str, Any]:
    """Initialize the game state based on loaded game data."""
    print("--- Initializing game state from loaded data ---")
    return {
        "current_card_id": None,
        "resources": game_data.get("game_settings", {}).get("initial_resources", {}).copy(),
        "cards": {card["id"]: card for card in game_data.get("cards", [])},
        "history": []
    }

def get_card(card_id: str) -> Optional[Dict[str, Any]]:
    """Helper function to get card by ID."""
    print(f"--- get_card called with: {card_id} ---")
    global GAME_STATE
    card: Optional[Dict[str, Any]] = GAME_STATE.get("cards", {}).get(card_id)
    return card

def handle_card_choice(card_id: str, choice_direction: str) -> Optional[str]:
    """Handle card choice, apply effects, update state, return next card ID."""
    print(f"--- handle_card_choice called: {card_id}, {choice_direction} ---")
    global GAME_STATE
    card = get_card(card_id)
    if not card:
        print(f"### handle_card_choice: Card {card_id} not found ###")
        return None
    choice = card.get("choices", {}).get(choice_direction)
    if not choice:
        print(f"### handle_card_choice: Choice {choice_direction} not found for card {card_id} ###")
        return None
    effects = choice.get("effects", {})
    print(f"--- Applying effects: {effects} ---")
    for resource, value in effects.items():
        if resource in GAME_STATE.get("resources", {}):
            GAME_STATE["resources"][resource] += value
        else:
             print(f"### Warning: Effect resource '{resource}' not found in game state ###")
    GAME_STATE.setdefault("history", []).append({
        "card_id": card_id, "choice": choice_direction, "effects": effects
    })
    next_card_id: Optional[str] = choice.get("next_card")
    print(f"--- Next card ID: {next_card_id} ---")
    GAME_STATE["current_card_id"] = next_card_id
    return next_card_id

# Restored main function logic
def main(page: Page) -> None:
    """Initialize the Flet app on the page."""
    global APP_CONFIG, GAME_DATA, GAME_STATE
    
    print("--- Starting main Flet function (Using JSON Paths Directly) ---")
    
    if page.client_storage.contains_key("current_screen"):
        page.client_storage.remove("current_screen")
        print("--- Cleared stored screen state ---")
        
    APP_CONFIG["platform"] = page.platform
    APP_CONFIG["version"] = page.app_version if hasattr(page, 'app_version') else APP_CONFIG.get("version", "?.?")
    
    GAME_DATA = load_game_data(APP_CONFIG["game_theme"])
    GAME_STATE = initialize_game_state(GAME_DATA)

    if GAME_DATA.get("error"):
        page.add(ft.Text(f"Error: {GAME_DATA.get('error')}", color=ft.colors.RED))
        page.update()
        return
        
    print(f"--- Actual game state loaded for theme: {APP_CONFIG['game_theme']} ---")
    
    page.title = f"SwipeVerse"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK
    
    if page.platform in ["android", "ios"]:
        page.window_width = 400
        page.window_height = 800
    else:
        page.window_width = 500
        page.window_height = 750

    current_screen = "title"
    
    main_container = ft.Container(
        expand=True, content=None, alignment=ft.alignment.center
    )
    
    resource_indicators_row = ft.Row(
        controls=[], alignment=ft.MainAxisAlignment.CENTER, spacing=10
    )
    
    # --- Restore update_resource_indicators logic --- 
    def update_resource_indicators():
        """Rebuilds the resource indicators row based on current GAME_STATE."""
        global GAME_DATA, GAME_STATE
        print("--- Updating resource indicators ---")
        resource_icons = GAME_DATA.get("theme", {}).get("resource_icons", {})
        indicators = []
        for name, value in GAME_STATE.get("resources", {}).items():
            # Use path directly from JSON data
            icon_path = resource_icons.get(name, '') 
            print(f"    Icon path used: {icon_path}") 
            indicators.append(
                ft.Container(
                    content=ft.Stack([
                        ft.Image(
                            src=icon_path, width=40, height=40,
                            fit=ft.ImageFit.CONTAIN,
                            error_content=ft.Icon(ft.icons.BROKEN_IMAGE_OUTLINED, size=30),
                        ),
                        ft.Container(
                            width=40, height=40 * (1 - min(max(value, 0), 100) / 100),
                            bgcolor=ft.colors.with_opacity(0.6, ft.colors.BLACK),
                            alignment=ft.alignment.top_center,
                        )
                    ]),
                    width=50, height=50, tooltip=f"{name.capitalize()}: {value}", margin=3,
                )
            )
        resource_indicators_row.controls = indicators
        print(f"--- Resource indicators updated with {len(indicators)} controls ---")

    # --- Screen Navigation --- 
    def navigate_to(screen_name, container):
        nonlocal current_screen
        current_screen = screen_name
        page.client_storage.set("current_screen", screen_name)
        print(f"--- Navigating to: {screen_name} ---")
        container.content = None
        # page.clean() # Keep commented out
        if screen_name == "title":
            show_title_screen(container)
        elif screen_name == "game":
            show_game_screen(container)
        elif screen_name == "settings":
            show_settings_screen(container)
        elif screen_name == "achievements":
            show_achievements_screen(container)
        else:
            show_title_screen(container)
        print(f"--- Content set for: {screen_name} ---")
        page.update()
        print(f"--- Page updated after navigating to: {screen_name} ---")

    # --- Screen Definitions (Full logic) --- 
    def show_title_screen(container):
        """Builds and displays the original title screen."""
        print("--- Building ORIGINAL title screen ---")
        title_content = ft.Column(
            controls=[
                ft.Text("SwipeVerse", size=40, weight=ft.FontWeight.BOLD),
                ft.Text("A card-based decision game", size=20),
                ft.Container(height=20),
                ft.ElevatedButton("Start Game", width=200, on_click=lambda e: navigate_to("game", container)),
                ft.ElevatedButton("Settings", width=200, on_click=lambda e: navigate_to("settings", container)),
                ft.ElevatedButton("Achievements", width=200, on_click=lambda e: navigate_to("achievements", container)),
                ft.Container(height=10),
                ft.Text(f"Version {APP_CONFIG.get('version', '?.?')}", size=12, italic=True, color=ft.colors.GREY_500),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER, spacing=12, expand=True,
        )
        container.content = title_content
        print("--- Original title screen content set ---")

    def show_game_screen(container):
        """Builds and displays the main game screen (Restored)."""
        global GAME_STATE, GAME_DATA
        
        print("--- Building GAME screen ---")
        
        if not GAME_STATE.get("current_card_id") and GAME_DATA.get("cards"):
            first_card_id = next(iter(GAME_STATE.get("cards", {})), None)
            if first_card_id:
                GAME_STATE["current_card_id"] = first_card_id
                print(f"--- Starting game with first card: {first_card_id} ---")
            else:
                 print("### Error: No cards found in game data ###")
                 container.content = ft.Column([
                     ft.Text("Error: No cards defined.", color=ft.colors.RED, size=18),
                     ft.ElevatedButton("Back to Menu", on_click=lambda e: navigate_to("title", container))
                 ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                 return
                
        current_card = get_card(GAME_STATE.get("current_card_id", ""))
        
        card_display_area = ft.Column( 
            controls=[], 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True, 
        )
        header_container = ft.Container(
            content=None, 
            padding=10,
            bgcolor=ft.colors.SURFACE_VARIANT,
        )
        
        card_controls = []
        if not current_card:
            print("--- No current card, showing Game Over / No Cards screen ---")
            card_controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("Game Over" if GAME_STATE.get("history") else "No more cards!", size=24, weight=ft.FontWeight.BOLD),
                        ft.Text("Thanks for playing!" if GAME_STATE.get("history") else "You've reached the end."),
                        ft.Container(height=20),
                        ft.ElevatedButton("Back to Menu", on_click=lambda e: navigate_to("title", container)),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=20,
                    border_radius=10,
                    width=300,
                    alignment=ft.alignment.center,
                )
            )
        else:
            # Use path directly from JSON data
            card_image_path = current_card.get("image", "")
            print(f"--- Building card display for: {current_card.get('id')} Image path used: {card_image_path} ---") 
            
            card_inner_content = ft.Column([
                ft.Text(current_card.get("title", ""), size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Container(
                    content=ft.Image(
                        src=card_image_path, 
                        height=150,
                        fit=ft.ImageFit.CONTAIN,
                        error_content=ft.Container( 
                            height=150, 
                            alignment=ft.alignment.center, 
                            content=ft.Icon(ft.icons.IMAGE_NOT_SUPPORTED_OUTLINED, color=ft.colors.GREY_500, size=40)
                        ),
                        border_radius=ft.border_radius.all(8),
                    ), 
                    padding=ft.padding.symmetric(vertical=10)
                ) if card_image_path else ft.Container(height=10), 
                ft.Text(current_card.get("text", ""), size=16, text_align=ft.TextAlign.CENTER, selectable=True),
            ], spacing=8, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            
            card_inner_container = ft.Container(
                content=card_inner_content,
                padding=15,
                bgcolor=ft.colors.SURFACE_VARIANT,
                border_radius=10,
                width=300,
                alignment=ft.alignment.center,
                border=ft.border.all(1, ft.colors.with_opacity(0.1, ft.colors.WHITE)),
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=5,
                    color=ft.colors.with_opacity(0.1, ft.colors.BLACK),
                    offset=ft.Offset(2, 2),
                )
            )

            drag_container = ft.Container(
                content=card_inner_container,
                width=320, 
                alignment=ft.alignment.center,
                animate_offset=ft.animation.Animation(200, ft.AnimationCurve.EASE_OUT),
                animate_rotation=ft.animation.Animation(200, ft.AnimationCurve.EASE_OUT),
                animate_opacity=ft.animation.Animation(200, ft.AnimationCurve.EASE_OUT),
            )

            swipe_state = {"distance": 0}
            swipe_threshold = 80
            max_swipe_angle = 8
            max_offset = 120
            
            def handle_drag_update(e: ft.DragUpdateEvent):
                state = swipe_state
                state["distance"] += e.delta_x
                clamped_distance = min(max(state["distance"], -max_offset*1.5), max_offset*1.5)
                normalized_distance = min(abs(clamped_distance) / swipe_threshold, 1)
                rotation_rad = (clamped_distance / max_offset) * (max_swipe_angle * (3.14159 / 180))
                offset_x = clamped_distance / drag_container.width if drag_container.width else 0
                drag_container.offset = ft.transform.Offset(offset_x, 0)
                drag_container.rotate = ft.transform.Rotate(angle=rotation_rad, alignment=ft.alignment.center)
                drag_container.opacity = 1.0 - (normalized_distance * 0.3)
                page.update()

            def handle_drag_end(e: ft.DragEndEvent):
                state = swipe_state
                final_distance = state["distance"]
                state["distance"] = 0

                if abs(final_distance) > swipe_threshold:
                    direction = "right" if final_distance > 0 else "left"
                    final_offset_x = 1.5 if direction == "right" else -1.5 
                    final_rotation = max_swipe_angle if direction == "right" else -max_swipe_angle
                    final_rotation_rad = final_rotation * (3.14159 / 180)
                    
                    drag_container.offset = ft.transform.Offset(final_offset_x, 0)
                    drag_container.rotate = ft.transform.Rotate(angle=final_rotation_rad, alignment=ft.alignment.center)
                    drag_container.opacity = 0
                    page.update() 
                    
                    process_choice(direction)
                    
                else:
                    drag_container.offset = ft.transform.Offset(0, 0)
                    drag_container.rotate = ft.transform.Rotate(0)
                    drag_container.opacity = 1.0
                    page.update()
            
            card_gesture_detector = ft.GestureDetector(
                mouse_cursor=ft.MouseCursor.MOVE,
                drag_interval=10,
                on_horizontal_drag_update=handle_drag_update,
                on_horizontal_drag_end=handle_drag_end,
                content=drag_container,
            )
            
            card_controls.append(card_gesture_detector)

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
                )
            )
        
        def process_choice(direction):
            global GAME_STATE, GAME_DATA
            current_card_id = GAME_STATE.get("current_card_id")
            if not current_card_id:
                 print("### Error: process_choice called with no current card ID ###")
                 return
                 
            print(f"--- Processing choice '{direction}' for card {current_card_id} ---")
            processed_card = get_card(current_card_id)
            handle_card_choice(current_card_id, direction)
            choice_data = processed_card.get("choices", {}).get(direction, {}) if processed_card else {}
            effects = choice_data.get("effects", {})
            effect_text = ", ".join([f"{k.capitalize()}: {v:+d}" for k, v in effects.items()]) if effects else "No effect"
            
            # Correct way to show Snackbar
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"{choice_data.get('text', direction.capitalize())}. {effect_text}"),
                duration=2500
            )
            page.snack_bar.open = True
            
            print("--- Choice processed, rebuilding game screen for next state ---")
            show_game_screen(container)
            page.update()
            
        # --- Assemble Game Screen --- 
        header_container.content = ft.Row([
                ft.IconButton(ft.icons.ARROW_BACK, tooltip="Back to Menu", on_click=lambda e: navigate_to("title", container)),
                ft.Text(GAME_DATA.get("game_info", {}).get("title", "Game"), size=20, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),
                ft.Container(width=40) # Balance the back button space
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        update_resource_indicators() # Update the globally defined row
        card_display_area.controls = card_controls 

        container.content = ft.Column([
            header_container,
            resource_indicators_row, # Use the globally defined row
            ft.Container(height=10),
            card_display_area, 
            ft.Container(height=20), # Bottom padding
        ], expand=True, spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        print("--- Game screen content assembled and SET IN CONTAINER ---")

    def show_settings_screen(container): 
        print("--- show_settings_screen called (placeholder) ---")
        container.content = ft.Column([
            ft.Text("Settings Placeholder", color=ft.colors.WHITE),
            ft.ElevatedButton("Back", on_click=lambda e: navigate_to("title", container))
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    def show_achievements_screen(container): 
        print("--- show_achievements_screen called (placeholder) ---")
        container.content = ft.Column([
            ft.Text("Achievements Placeholder", color=ft.colors.WHITE),
            ft.ElevatedButton("Back", on_click=lambda e: navigate_to("title", container))
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # --- Initial Setup --- 
    print("--- Adding main_container to page... ---")
    page.add(main_container)
    print("--- Navigating to initial screen... ---")
    navigate_to(current_screen, main_container)

    print("--- Flet app main function complete (Using JSON Paths Directly). ---")
