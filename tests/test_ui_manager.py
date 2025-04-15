import os
import sys
import pytest
from pytest_mock import MockerFixture

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import flet as ft
from swipe_fate.ui.ui_manager import UIManager
from swipe_fate.core.game_state import GameState
from swipe_fate.core.event import Event

class TestUIManager:
    @pytest.fixture
    def mock_page(self, mocker: MockerFixture):
        return mocker.Mock(spec=ft.Page)
    
    @pytest.fixture
    def game_state(self):
        return GameState()
    
    @pytest.fixture
    def ui_manager(self, mock_page, game_state):
        return UIManager(mock_page, game_state)
    
    def test_update_score_display(self, ui_manager):
        # Create a mock event with score data
        event = Event("score_changed", {"new_score": 100})
        
        # Call the method
        ui_manager.update_score_display(event)
        
        # Check if score label was updated
        assert ui_manager.score_label.value == "Score: 100"
        
    def test_increase_score(self, ui_manager, game_state, mocker: MockerFixture):
        # Mock the event
        mock_event = mocker.Mock()
        
        # Initial score should be 0
        assert game_state.score == 0
        
        # Call increase_score
        ui_manager.increase_score(mock_event)
        
        # Score should be incremented
        assert game_state.score == 1