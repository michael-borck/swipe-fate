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

# Function definitions (Restored - Minimal Implementations)
def load_game_data(game_theme: str) -> Dict[str, Any]:
    print(f"--- load_game_data called with: {game_theme} ---")
    # Minimal load to check structure, no real data yet
    # In a real step, this would load from JSON
    return {"game_info": {"title": "Minimal Loaded Game"}, "theme": {}, "game_settings": {"initial_resources": {}}, "cards": []}

def initialize_game_state(game_data: Dict[str, Any]) -> Dict[str, Any]:
    print(f"--- initialize_game_state called ---")
    return {"current_card_id": None, "resources": {}, "cards": {}, "history": []}

def get_card(card_id: str) -> Optional[Dict[str, Any]]:
    print(f"--- get_card called with: {card_id} ---")
    return None

def handle_card_choice(card_id: str, choice_direction: str) -> Optional[str]:
    print(f"--- handle_card_choice called with: {card_id}, {choice_direction} ---")
    return None

def update_resource_indicators(): 
    print("--- update_resource_indicators called (pass) ---")
    pass

def show_game_screen(container): 
    print("--- show_game_screen called (placeholder) ---")
    container.content = ft.Text("Game Placeholder", color=ft.colors.WHITE)
    pass

def show_settings_screen(container): 
    print("--- show_settings_screen called (placeholder) ---")
    container.content = ft.Text("Settings Placeholder", color=ft.colors.WHITE)
    pass

def show_achievements_screen(container): 
    print("--- show_achievements_screen called (placeholder) ---")
    container.content = ft.Text("Achievements Placeholder", color=ft.colors.WHITE)
    pass

# Restored main function logic
def main(page: Page) -> None:
    """Initialize the Flet app on the page."""
    global APP_CONFIG, GAME_DATA, GAME_STATE
    
    print("--- Starting main Flet function (Restored Logic) ---")
    
    # Clear stored screen state if it exists
    if page.client_storage.contains_key("current_screen"):
        page.client_storage.remove("current_screen")
        print("--- Cleared stored screen state ---")
        
    APP_CONFIG["platform"] = page.platform
    APP_CONFIG["version"] = page.app_version if hasattr(page, 'app_version') else APP_CONFIG.get("version", "?.?")
    
    # Call minimal load/init functions
    GAME_DATA = load_game_data(APP_CONFIG["game_theme"])
    GAME_STATE = initialize_game_state(GAME_DATA)

    if GAME_DATA.get("error"):
        page.add(ft.Text(f"Error: {GAME_DATA.get('error')}", color=ft.colors.RED))
        page.update()
        return
        
    print(f"--- Minimal game state loaded for theme: {APP_CONFIG['game_theme']} ---")
    
    page.title = f"SwipeVerse"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK
    
    # Restore window size logic
    if page.platform in ["android", "ios"]:
        page.window_width = 400
        page.window_height = 800
    else:
        page.window_width = 500
        page.window_height = 750

    current_screen = "title" # Default to title
    
    main_container = ft.Container(
        expand=True, content=None, alignment=ft.alignment.center
    )
    
    # Resource row defined but not used yet
    resource_indicators_row = ft.Row(
        controls=[], alignment=ft.MainAxisAlignment.CENTER, spacing=10
    )

    # --- Screen Navigation --- 
    def navigate_to(screen_name, container):
        nonlocal current_screen
        current_screen = screen_name
        page.client_storage.set("current_screen", screen_name)
        print(f"--- Navigating to: {screen_name} ---")
        container.content = None
        # page.clean() # <--- Commenting out AGAIN
        if screen_name == "title":
            show_title_screen(container) # Function def exists but is minimal
        elif screen_name == "game":
            show_game_screen(container) # Function def exists but is minimal
        elif screen_name == "settings":
            show_settings_screen(container) # Function def exists but is minimal
        elif screen_name == "achievements":
            show_achievements_screen(container) # Function def exists but is minimal
        else:
            show_title_screen(container) # Default to title
        print(f"--- Content placeholder set for: {screen_name} ---")
        page.update()
        print(f"--- Page updated after navigating to: {screen_name} ---")

    # --- Screen Definitions (Minimal) --- 
    def show_title_screen(container):
        print("--- Building MINIMAL title screen ---")
        title_content = ft.Column(
            controls=[
                ft.Text("Minimal Title Screen", color=ft.colors.WHITE, size=20),
                # Add buttons that call navigate_to
                ft.ElevatedButton("Go Game (Placeholder)", on_click=lambda e: navigate_to("game", container)),
                ft.ElevatedButton("Go Settings (Placeholder)", on_click=lambda e: navigate_to("settings", container)),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        container.content = title_content
        print("--- Minimal title screen content set ---")

    # --- Initial Setup --- 
    print("--- Adding main_container to page... ---")
    page.add(main_container)
    print("--- Navigating to initial screen... ---")
    navigate_to(current_screen, main_container)

    print("--- Flet app main function complete (Restored Logic). ---")
