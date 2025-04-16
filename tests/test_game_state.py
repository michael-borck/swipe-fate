import pytest

from swipe_verse.models.config import Card, CardChoice, GameConfig, GameSettings, Theme
from swipe_verse.models.game_state import GameState


@pytest.fixture
def sample_config():
    """Create a sample game config for testing"""
    return GameConfig(
        game_info={
            "title": "Test Game",
            "description": "Test game description",
            "version": "1.0.0",
            "author": "Test Author",
        },
        theme=Theme(
            name="Test Theme",
            card_back="card_back.png",
            color_scheme={
                "primary": "#000000",
                "secondary": "#ffffff",
                "accent": "#ff0000",
            },
            resource_icons={
                "resource1": "resource1.png",
                "resource2": "resource2.png",
            },
            filters={"default": ["none"], "available": ["grayscale"]},
        ),
        game_settings=GameSettings(
            initial_resources={"resource1": 50, "resource2": 50},
            win_conditions=[{"resource": "resource1", "min": 10, "max": 90}],
            difficulty_modifiers={"easy": 0.7, "standard": 1.0, "hard": 1.3},
            turn_unit="years",
            stats={"popularity_formula": "resource1*0.5 + resource2*0.5"},
        ),
        cards=[
            Card(
                id="card_001",
                title="Test Card 1",
                text="Test card text 1",
                image="card1.png",
                choices={
                    "left": CardChoice(
                        text="Left choice",
                        effects={"resource1": 10},
                        next_card="card_002",
                    ),
                    "right": CardChoice(
                        text="Right choice",
                        effects={"resource2": -5},
                    ),
                },
            ),
            Card(
                id="card_002",
                title="Test Card 2",
                text="Test card text 2",
                image="card2.png",
                choices={
                    "left": CardChoice(
                        text="Left choice 2",
                        effects={"resource1": -5},
                        next_card="card_001",
                    ),
                    "right": CardChoice(
                        text="Right choice 2",
                        effects={"resource2": 10},
                    ),
                },
            ),
        ],
    )


def test_game_state_initialization(sample_config):
    """Test basic initialization of a GameState"""
    # Arrange
    resources = {"resource1": 50, "resource2": 50}
    card = sample_config.cards[0]
    
    # Act
    game_state = GameState(
        resources=resources,
        current_card=card,
        settings=sample_config.game_settings,
        theme=sample_config.theme,
    )
    
    # Assert
    assert game_state.resources == resources
    assert game_state.current_card == card
    assert game_state.settings == sample_config.game_settings
    assert game_state.theme == sample_config.theme
    assert game_state.turn_count == 0
    assert game_state.seen_cards == set()
    assert game_state.difficulty == "standard"
    assert game_state.player_name == "Player"
    assert not game_state.game_over
    assert game_state.end_message == ""


def test_new_game(sample_config, mocker):
    """Test creating a new game state from configuration"""
    # Arrange
    mock_random = mocker.patch("random.choice", return_value=sample_config.cards[0])
    
    # Act
    game_state = GameState.new_game(
        config=sample_config,
        player_name="Test Player",
        difficulty="hard",
    )
    
    # Assert
    assert game_state.player_name == "Test Player"
    assert game_state.difficulty == "hard"
    assert game_state.resources == {"resource1": 50, "resource2": 50}
    assert game_state.current_card == sample_config.cards[0]
    assert game_state.turn_count == 0
    assert game_state.seen_cards == set()
    mock_random.assert_called_once_with(sample_config.cards)


def test_save_game(sample_config):
    """Test saving a game state to a dictionary"""
    # Arrange
    game_state = GameState.new_game(sample_config)
    game_state.turn_count = 5
    game_state.seen_cards = {"card_001", "card_002"}
    game_state.game_over = True
    game_state.end_message = "Game Over!"
    
    # Act
    save_data = game_state.save_game()
    
    # Assert
    assert save_data["resources"] == game_state.resources
    assert save_data["current_card_id"] == game_state.current_card.id
    assert save_data["turn_count"] == 5
    assert set(save_data["seen_cards"]) == {"card_001", "card_002"}
    assert save_data["difficulty"] == "standard"
    assert save_data["player_name"] == "Player"
    assert save_data["game_over"] == True
    assert save_data["end_message"] == "Game Over!"


def test_load_game_card_found(sample_config):
    """Test loading a game state from saved data when card is found"""
    # Arrange
    save_data = {
        "resources": {"resource1": 25, "resource2": 75},
        "current_card_id": "card_002",
        "turn_count": 10,
        "seen_cards": ["card_001", "card_002"],
        "difficulty": "easy",
        "player_name": "Saved Player",
        "game_over": False,
        "end_message": "",
    }
    
    # Act
    game_state = GameState.load_game(save_data, sample_config)
    
    # Assert
    assert game_state.resources == {"resource1": 25, "resource2": 75}
    assert game_state.current_card.id == "card_002"
    assert game_state.turn_count == 10
    assert game_state.seen_cards == {"card_001", "card_002"}
    assert game_state.difficulty == "easy"
    assert game_state.player_name == "Saved Player"
    assert not game_state.game_over
    assert game_state.end_message == ""


def test_load_game_card_not_found(sample_config, mocker):
    """Test loading a game state from saved data when card is not found"""
    # Arrange
    save_data = {
        "resources": {"resource1": 25, "resource2": 75},
        "current_card_id": "non_existent_card",
        "turn_count": 10,
        "seen_cards": ["card_001", "card_002"],
        "difficulty": "easy",
        "player_name": "Saved Player",
        "game_over": False,
        "end_message": "",
    }
    
    # Mock random.choice to return a specific card
    mock_random = mocker.patch("random.choice", return_value=sample_config.cards[0])
    
    # Act
    game_state = GameState.load_game(save_data, sample_config)
    
    # Assert
    assert game_state.resources == {"resource1": 25, "resource2": 75}
    assert game_state.current_card == sample_config.cards[0]
    assert game_state.turn_count == 10
    assert game_state.seen_cards == {"card_001", "card_002"}
    assert game_state.difficulty == "easy"
    assert game_state.player_name == "Saved Player"
    assert not game_state.game_over
    assert game_state.end_message == ""
    mock_random.assert_called_once_with(sample_config.cards)