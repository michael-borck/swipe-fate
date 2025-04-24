import flet as ft
from flet import Page

def main(page: Page) -> None:
    print("--- Starting ABSOLUTE MINIMAL main function ---")
    page.title = "Absolute Minimal Test"
    page.add(ft.Text("Hello from absolute minimal main.py!", color=ft.colors.WHITE))
    page.update()
    print("--- Absolute Minimal main function complete. ---")
