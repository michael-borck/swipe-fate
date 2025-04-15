import flet as ft
from typing import Any, Callable
from swipe_fate.core.game_state import GameState
from swipe_fate.core.event import Event

class UIManager:
    def __init__(self, page: ft.Page, game_state: GameState) -> None:
        self.page = page
        self.game_state = game_state
        self.score_label = ft.TextField(value=f"Score: {self.game_state.score}", text_align=ft.TextAlign.CENTER)
        self.increment_button = ft.TextButton(text="Increase Score", on_click=self.increase_score)

    def setup_ui(self) -> None:
        # This could be dynamically changed or loaded from a database, file, etc.
        decision = {
            'description': "Choose your direction:",
            'left': "Go Left",
            'right': "Go Right"
        }

        # Create a card with text and two buttons
        card = ft.Card(
        content=ft.Column([
            ft.Text(decision['description'], size=20),
            ft.Row([
                ft.TextButton(decision['left'], on_click=lambda e: self.handle_click(e, 'Left')),
                ft.TextButton(decision['right'], on_click=lambda e: self.handle_click(e, 'Right'))
            ], alignment="spaceAround")
        ]),
        width=300
        )

        # Add the card to the page
        self.page.add(card)

    def handle_click(self, event: ft.ControlEvent, direction: str) -> None:
        # Update the card content or do something else based on the button clicked
        if isinstance(event.control.parent.parent.children[0], ft.Text):
            event.control.parent.parent.children[0].value = f"You chose to go {direction}!"
            self.page.update()

    def increase_score(self, e: ft.ControlEvent) -> None:
        new_score = self.game_state.increment_score()
        self.page.update_controls([self.score_label.update(value=f"Score: {new_score}")])

    def update_score_display(self, event: Event) -> None:
        if event.data and 'new_score' in event.data:
            self.score_label.value = f"Score: {event.data['new_score']}"
            self.page.update()