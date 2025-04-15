import flet as ft
from swipe_fate.core.core_engine import CoreEngine

def main(page: ft.Page):
    """Main entry point for the application"""
    # Configure default page settings
    page.title = "SwipeFate"
    page.bgcolor = "#FFFFFF"  # Bright white background
    page.padding = 10
    page.window_width = 500
    page.window_height = 800
    page.window_resizable = True
    page.window_maximizable = True
    
    # Add a simple loading indicator as first element
    page.add(ft.Text("Loading SwipeFate...", size=30, color="red", weight="bold"))
    page.update()
    
    print("Main function started, page initialized with loading text")
    
    # Create and start the game engine
    engine = CoreEngine(page)
    engine.run()
    
    print("Game engine initialized and running")

if __name__ == "__main__":
    ft.app(target=main)