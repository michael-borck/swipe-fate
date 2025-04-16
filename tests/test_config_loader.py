import json
import os
import tempfile

import pytest

from swipe_fate.models.config import GameConfig
from swipe_fate.services.config_loader import ConfigLoader


@pytest.fixture
def sample_config():
    return {
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
            }
        ],
    }


@pytest.fixture
def config_file(sample_config):
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as temp:
        json.dump(sample_config, temp)
        temp_path = temp.name

    yield temp_path

    # Clean up the temp file
    os.unlink(temp_path)


@pytest.mark.asyncio
async def test_load_config_from_file(config_file, sample_config):
    # Arrange
    loader = ConfigLoader()

    # Act
    config = await loader.load_config(config_file)

    # Assert
    assert isinstance(config, GameConfig)
    assert config.game_info.title == sample_config["game_info"]["title"]
    assert len(config.cards) == len(sample_config["cards"])
    assert config.cards[0].id == sample_config["cards"][0]["id"]
    assert config.game_settings.turn_unit == sample_config["game_settings"]["turn_unit"]


@pytest.mark.asyncio
async def test_merge_configs(sample_config):
    # Arrange
    loader = ConfigLoader()
    base_config = GameConfig.model_validate(sample_config)
    override = {"game_info": {"title": "Overridden Title"}}

    # Act
    merged = await loader.merge_configs(base_config, override)

    # Assert
    assert merged.game_info.title == "Overridden Title"
    assert merged.game_info.description == base_config.game_info.description
