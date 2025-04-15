import flet as ft
from swipe_fate.core.core_engine import CoreEngine

def main(page: ft.Page):
    """Main entry point for the application"""
    # Configure default page settings
    page.title = "SwipeFate"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 400
    page.window_height = 700
    page.window_resizable = True
    page.window_maximizable = False
    
    # Create and start the game engine
    engine = CoreEngine(page)
    engine.run()

if __name__ == "__main__":
    ft.app(target=main)