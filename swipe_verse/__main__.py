#!/usr/bin/env python
"""Main entry point for SwipeVerse using standard Flet ft.app()."""

import flet as ft
from swipe_verse.main import main as app_main  # Import the main function from main.py


def main():
    """Runs the Flet application."""
    # Note: assets_dir here should be relative to the project root when running
    # 'flet run' or building. Flet handles packaging these.
    ft.app(target=app_main, assets_dir="swipe_verse/assets")


if __name__ == "__main__":
    main()
