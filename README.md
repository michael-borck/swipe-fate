# Swipe Verse

A multiverse card-based decision game built with Python and Flet.

## Overview

Swipe Verse is a theme-based card decision game where players navigate different realities by swiping left or right on cards, managing various resources to succeed across multiple thematic universes. Originally inspired by "Reigns", the game has evolved into a multiverse of interconnected experiences, from medieval kingdoms to corporate boardrooms and beyond. Built using Flet, a Python framework for cross-platform applications.

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
git clone https://github.com/yourusername/swipe-verse.git
cd swipe-verse

# Install with pip
pip install -e .
```

## Usage

```bash
# Run the game with default settings
swipe-verse

# Run with a custom configuration file
swipe-verse --config path/to/config.json

# Run in terminal UI mode
swipe-verse --mode tui

# Run with custom assets
swipe-verse --assets path/to/assets/folder

# Run with a specific theme
swipe-verse --theme business  # or kingdom, tutorial, etc.

# Start with the tutorial
swipe-verse --theme tutorial
```

## Game Configuration

The game is data-driven and can be customized by editing JSON configuration files. Multiple theme configurations are available in the `swipe_verse/config/` directory:

- `kingdom_game.json` - Medieval kingdom management
- `business_game.json` - Corporate leadership simulation
- `tutorial_game.json` - Interactive guide to gameplay mechanics

### Example Configuration

```json
{
  "game_info": {
    "title": "Kingdom Verse",
    "description": "Rule your medieval realm through the power of swiping",
    "backstory": "The old king has died without an heir, and you've been unexpectedly chosen to rule...",
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
mypy swipe_verse

# Run tests
pytest
```

## License

MIT

## Credits

- Inspired by the game [Reigns](https://www.devolverdigital.com/games/reigns)
- Built with [Flet](https://flet.dev/)