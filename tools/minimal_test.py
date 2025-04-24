import flet as ft

def main(page: ft.Page):
    page.title = "Minimal Test"
    page.add(ft.Text("Hello, Flet!"))
    page.update()

ft.app(target=main)
