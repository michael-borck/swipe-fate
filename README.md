# Swipe Fate

A "Reigns-like" card-based decision game built with Python and Flet.

## Overview

Swipe Fate is a data-driven card-based decision game where players make choices by swiping left or right on cards, managing various resources to stay in power as long as possible. The game is built using Flet, a Python framework for building cross-platform applications.

## Features

- **Card-based gameplay** similar to "Reigns"
- **Resource management** system with visual indicators
- **Data-driven approach** with game content loaded from JSON configuration files
- **Cross-platform support** for desktop, mobile, and web
- **Mobile-first responsive design** that works on any screen size
- **Customizable themes** and visual filters

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/swipe-fate.git
cd swipe-fate

# Install with pip
pip install -e .
```

## Usage

```bash
# Run the game with default settings
swipe-fate

# Run with a custom configuration file
swipe-fate --config path/to/config.json

# Run in terminal UI mode
swipe-fate --mode tui

# Run with custom assets
swipe-fate --assets path/to/assets/folder
```

## Game Configuration

The game is data-driven and can be customized by editing JSON configuration files. See the `swipe_fate/config/default_game.json` file for an example.

### Example Configuration

```json
{
  "game_info": {
    "title": "Swipe Fate",
    "description": "Rule your kingdom through the power of swiping",
    "version": "0.1.0",
    "author": "Your Name"
  },
  "theme": {
    "name": "Default Theme",
    "card_back": "assets/default/card_back.png",
    "background": null,
    "color_scheme": {
      "primary": "#4a4a4a",
      "secondary": "#f5f5f5",
      "accent": "#3273dc"
    },
    "resource_icons": {
      "resource1": "assets/default/resource_icons/resource1.png",
      "resource2": "assets/default/resource_icons/resource2.png"
    },
    "filters": {
      "default": "none",
      "available": ["grayscale", "cartoon", "oil_painting"]
    }
  },
  "game_settings": {
    "initial_resources": {
      "resource1": 50,
      "resource2": 50
    },
    "win_conditions": [
      {"resource": "resource1", "min": 10, "max": 90}
    ],
    "difficulty_modifiers": {
      "easy": 0.7,
      "standard": 1.0,
      "hard": 1.3
    }
  },
  "cards": [
    {
      "id": "card_001",
      "title": "First Decision",
      "text": "This is the situation you're facing. What will you do?",
      "image": "path/to/card_image.png",
      "choices": {
        "left": {
          "text": "Option A",
          "effects": {
            "resource1": 10,
            "resource2": -5
          },
          "next_card": "card_002"
        },
        "right": {
          "text": "Option B",
          "effects": {
            "resource1": -5,
            "resource2": 10
          }
        }
      }
    }
  ]
}
```

## Development

This project uses:
- [Flet](https://flet.dev/) for UI
- [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation
- [Ruff](https://github.com/charliermarsh/ruff) for linting
- [mypy](http://mypy-lang.org/) for type checking
- [pytest](https://docs.pytest.org/) for testing

### Development Setup

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run linting
ruff check .

# Run type checking
mypy swipe_fate

# Run tests
pytest
```

## License

MIT

## Credits

- Inspired by the game [Reigns](https://www.devolverdigital.com/games/reigns)
- Built with [Flet](https://flet.dev/)