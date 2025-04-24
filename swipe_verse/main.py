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
    "assets_dir": "swipe_verse/assets",
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
            # Restore path adjustment logic
            theme_data = data.get("theme", {})
            if "card_back" in theme_data and isinstance(theme_data["card_back"], str):
                 theme_data["card_back"] = str(Path("swipe_verse") / theme_data["card_back"]) 
            resource_icons = theme_data.get("resource_icons", {})
            for key, path in resource_icons.items():
                 if isinstance(path, str):
                     resource_icons[key] = str(Path("swipe_verse") / path)
            cards_data = data.get("cards", [])
            for card in cards_data:
                if "image" in card and isinstance(card["image"], str):
                    card["image"] = str(Path("swipe_verse") / card["image"])
            print("--- Adjusted asset paths in loaded data ---")
            return data
    except Exception as e:
        print(f"### Error loading/adjusting game data from {game_path}: {e} ###")
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
    
    print("--- Starting main Flet function (Restored Title Screen) ---")
    
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
    
    # Define resource row here to be accessible by update_resource_indicators
    resource_indicators_row = ft.Row(
        controls=[], alignment=ft.MainAxisAlignment.CENTER, spacing=10
    )
    
    # Restore update_resource_indicators logic
    def update_resource_indicators():
        """Rebuilds the resource indicators row based on current GAME_STATE."""
        global GAME_DATA, GAME_STATE
        print("--- Updating resource indicators ---")
        resource_icons = GAME_DATA.get("theme", {}).get("resource_icons", {})
        indicators = []
        for name, value in GAME_STATE.get("resources", {}).items():
            # Use adjusted path directly from GAME_DATA
            icon_path = resource_icons.get(name, '') 
            print(f"    Icon path: {icon_path}") # Debug print
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
        print(f"--- Content set for: {screen_name} ---") # Renamed log msg
        page.update()
        print(f"--- Page updated after navigating to: {screen_name} ---")

    # --- Screen Definitions (Restoring Title) --- 
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

    # Placeholder screen functions (as they were in the working state)
    def show_game_screen(container): 
        print("--- show_game_screen called (placeholder) ---")
        container.content = ft.Column([
            ft.Text("Game Placeholder", color=ft.colors.WHITE),
            ft.ElevatedButton("Back", on_click=lambda e: navigate_to("title", container))
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

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

    print("--- Flet app main function complete (Restored Title Screen). ---")
