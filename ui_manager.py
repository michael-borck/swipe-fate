import flet as ft

class UIManager:
    def __init__(self, page, game_state):
        self.page = page
        self.game_state = game_state
        self.score_label = ft.TextField(value=f"Score: {self.game_state.score}", text_align=ft.TextAlign.CENTER)
        self.increment_button = ft.TextButton(text="Increase Score", on_click=self.increase_score)

    #def setup_ui(self):
    #    self.page.add(self.score_label, self.increment_button)

    def main_view(self):
        return ft.Column([self.score_label, self.increment_button])

    def increase_score(self, e):
        new_score = self.game_state.increment_score()
        self.page.update_controls([self.score_label.update(value=f"Score: {new_score}")])

    def update_score_display(self, event):
        self.score_label.value = f"Score: {event.data['new_score']}"
        self.page.update()
