import flet as ft
from game_state import GameState
from ui_manager import UIManager
from event_manager import EventManager
from event import Event
from resource_loader import ResourceLoader

class CoreEngine:
    def __init__(self, page: ft.Page):
        self.page = page
        self.game_state = GameState()
        self.ui_manager = UIManager(self.page, self.game_state)
        self.event_manager = EventManager()

        self.setup()

    def setup(self):
        loader = ResourceLoader('config.json')
        self.decisions = loader.get_decisions()
        self.rules = loader.get_rules()
        self.events = loader.get_events()
        self.resources = loader.get_resources()
        self.themes = loader.get_themes()
        # self.ui_manager.setup_ui()
        self.event_manager.register_listener("score_changed", self.ui_manager.update_score_display)
        self.page.update()

    def run(self):
        self.page.add(self.ui_manager.main_view())
