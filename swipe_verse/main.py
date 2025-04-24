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

# Minimal main function (using globals implicitly)
def main(page: Page) -> None:
    print("--- Starting Minimal main function + Globals ---")
    page.title = f"Minimal Test + Globals (Theme: {APP_CONFIG.get('game_theme')})"
    page.add(ft.Text("Hello from minimal main.py + Globals!", color=ft.colors.WHITE))
    page.update()
    print("--- Minimal main + Globals complete. ---")
