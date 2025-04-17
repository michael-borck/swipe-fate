import pytest

from swipe_verse.models.config import GameConfig
from swipe_verse.models.game_state import GameState
from swipe_verse.services.game_logic import GameLogic


@pytest.fixture
def sample_config():
    return GameConfig.model_validate(
        {
            "game_info": {
                "title": "Test Game",
                "description": "Test game description",
                "version": "1.0.0",
                "author": "Test Author",
            },
            "theme": {
                "name": "Test Theme",
                "card_back": "card_back.png",
                "color_scheme": {
                    "primary": "#000000",
                    "secondary": "#ffffff",
                    "accent": "#ff0000",
                },
                "resource_icons": {
                    "resource1": "resource1.png",
                    "resource2": "resource2.png",
                },
                "filters": {"default": ["none"], "available": ["grayscale"]},
            },
            "game_settings": {
                "initial_resources": {"resource1": 50, "resource2": 50},
                "win_conditions": [{"resource": "resource1", "min": 10, "max": 90}],
                "difficulty_modifiers": {"easy": 0.7, "standard": 1.0, "hard": 1.3},
                "turn_unit": "years",
                "stats": {"popularity_formula": "resource1*0.5 + resource2*0.5"},
            },
            "cards": [
                {
                    "id": "card_001",
                    "title": "Test Card",
                    "text": "Test card text",
                    "image": "card.png",
                    "choices": {
                        "left": {
                            "text": "Left choice",
                            "effects": {"resource1": 10},
                            "next_card": "card_002",
                        },
                        "right": {"text": "Right choice", "effects": {"resource2": -5}},
                    },
                },
                {
                    "id": "card_002",
                    "title": "Test Card 2",
                    "text": "Test card text 2",
                    "image": "card2.png",
                    "choices": {
                        "left": {"text": "Left choice", "effects": {"resource1": -5}},
                        "right": {"text": "Right choice", "effects": {"resource2": 10}},
                    },
                },
            ],
        }
    )


def test_process_choice_left(sample_config, mocker):
    # Arrange
    # Mock the random choice to always return the first card in the config
    card_with_id_001 = [card for card in sample_config.cards if card.id == "card_001"][
        0
    ]
    mocker.patch("random.choice", return_value=card_with_id_001)

    game_state = GameState.new_game(sample_config)

    # Manually set the current card for test consistency
    game_state.current_card = card_with_id_001

    game_logic = GameLogic(game_state, sample_config)

    # Act
    result = game_logic.process_choice("left")

    # Assert
    assert not result.game_over
    assert game_state.resources["resource1"] == 60  # Initial 50 + 10 from left choice
    assert game_state.turn_count == 1
    assert game_state.current_card.id == "card_002"  # next_card is set to card_002


def test_process_choice_right(sample_config, mocker):
    # Arrange
    # Mock the random choice to always return the first card in the config
    card_with_id_001 = [card for card in sample_config.cards if card.id == "card_001"][
        0
    ]
    mocker.patch("random.choice", return_value=card_with_id_001)

    game_state = GameState.new_game(sample_config)

    # Manually set the current card for test consistency
    game_state.current_card = card_with_id_001

    game_logic = GameLogic(game_state, sample_config)

    # Act
    result = game_logic.process_choice("right")

    # Assert
    assert not result.game_over
    assert game_state.resources["resource2"] == 45  # Initial 50 - 5 from right choice
    assert game_state.turn_count == 1
    # No next_card specified for right choice, so random card selection happens
    # We mocked it to always be card_001
    assert game_state.current_card.id == "card_001"


def test_game_over_condition(sample_config):
    # Arrange
    game_state = GameState.new_game(sample_config)
    game_logic = GameLogic(game_state, sample_config)

    # Force resource to exceed max (90)
    game_state.resources["resource1"] = 95

    # Test the game over check directly
    game_over, message, won = game_logic._check_game_over()

    # Assert
    assert game_over
    assert "too high" in message.lower()


def test_popularity_calculation(sample_config):
    # Arrange
    game_state = GameState.new_game(sample_config)
    game_logic = GameLogic(game_state, sample_config)

    # Set resources to known values
    game_state.resources["resource1"] = 60
    game_state.resources["resource2"] = 40

    # Act
    popularity = game_logic.calculate_popularity()

    # Assert
    assert popularity == 50  # (60*0.5 + 40*0.5) = 50
