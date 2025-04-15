import flet as ft
from swipe_fate.core.core_engine import CoreEngine

def main(page: ft.Page):
    page.title = "SwipeFate"
    page.window_width = 400
    page.window_height = 650
    page.window_resizable = False
    page.theme_mode = ft.ThemeMode.SYSTEM
    
    engine = CoreEngine(page)
    engine.run()

if __name__ == "__main__":
    ft.app(target=main)