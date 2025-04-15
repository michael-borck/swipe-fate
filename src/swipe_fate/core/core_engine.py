import flet as ft
from typing import List, Dict, Any

from swipe_fate.core.game_state import GameState
from swipe_fate.ui.ui_manager import UIManager
from swipe_fate.core.event_manager import EventManager
from swipe_fate.core.event import Event
from swipe_fate.resource_loader import ResourceLoader

class CoreEngine:
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.game_state = GameState()
        self.ui_manager = UIManager(self.page, self.game_state)
        self.event_manager = EventManager()
        self.decisions: List[Dict[str, Any]] = []
        self.rules: List[Dict[str, Any]] = []
        self.events: List[Dict[str, Any]] = []
        self.resources: Dict[str, Any] = {}
        self.themes: Dict[str, Any] = {}
        self.setup()

    def setup(self) -> None:
        # Use path to configs folder
        loader = ResourceLoader('configs/business.json')
        self.decisions = loader.get_decisions()
        self.rules = loader.get_rules()
        self.events = loader.get_events()
        self.resources = loader.get_resources()
        self.themes = loader.get_themes()
        self.ui_manager.setup_ui()
        self.event_manager.register_listener("score_changed", self.ui_manager.update_score_display)
        self.page.update()

    def run(self) -> None:
        self.page.update()