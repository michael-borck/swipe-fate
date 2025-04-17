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

# Run with a specific game
swipe-verse --games business  # or kingdom, tutorial, etc.

# Start with the tutorial game
swipe-verse --games tutorial
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
    "title": "Kingdom Fate",
    "description": "Rule your medieval kingdom through the power of swiping",
    "version": "0.1.0",
    "author": "Swipe Fate Team",
    "license": "CC BY-SA 4.0",
    "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
    "backstory": "The old king has died without an heir, and to everyone's surprise, you've been chosen to rule the kingdom..."
  },
  "theme": {
    "name": "Kingdom Theme",
    "card_back": "assets/themes/kingdom/card_back.png",
    "background": null,
    "color_scheme": {
      "primary": "#4a4a4a",
      "secondary": "#f5f5f5",
      "accent": "#3273dc"
    },
    "resource_icons": {
      "treasury": "assets/themes/kingdom/resource_icons/treasury.png",
      "population": "assets/themes/kingdom/resource_icons/population.png",
      "military": "assets/themes/kingdom/resource_icons/military.png",
      "church": "assets/themes/kingdom/resource_icons/church.png"
    },
    "filters": {
      "default": "none",
      "available": ["grayscale", "cartoon", "oil_painting"]
    }
  },
  "game_settings": {
    "initial_resources": {
      "treasury": 50,
      "population": 50,
      "military": 50,
      "church": 50
    },
    "win_conditions": [
      { "resource": "treasury", "min": 10, "max": 90 },
      { "resource": "population", "min": 10, "max": 90 },
      { "resource": "military", "min": 10, "max": 90 },
      { "resource": "church", "min": 10, "max": 90 }
    ],
    "difficulty_modifiers": {
      "easy": 0.7,
      "standard": 1.0,
      "hard": 1.3
    },
    "turn_unit": "years",
    "stats": {
      "popularity_formula": "treasury*0.2 + population*0.3 + military*0.2 + church*0.3"
    }
  },
  "cards": [
    {
      "id": "card_001",
      "title": "The Harvest",
      "text": "This year's harvest is meager. Should you raise taxes to compensate or distribute grain from the royal reserves?",
      "image": "assets/themes/kingdom/card_fronts/card1.png",
      "choices": {
        "left": {
          "text": "Raise taxes",
          "effects": {
            "treasury": 15,
            "population": -10,
            "military": 0,
            "church": -5
          },
          "next_card": "card_002"
        },
        "right": {
          "text": "Distribute grain",
          "effects": {
            "treasury": -10,
            "population": 15,
            "military": 5,
            "church": 0
          },
          "next_card": "card_003"
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
# Install dev dependencies (using uv to manage your environment)
uv pip install -e ".[dev]"

# Run linting
ruff check .

# Run type checking
mypy swipe_verse

# Run tests
pytest
```

### Pre-commit Hooks

Use pre-commit to automatically format, lint, and type-check code before commits.

```bash
# Install pre-commit into your environment
uv pip install pre-commit

# Install Git hook scripts
uv pre-commit install

# Run all hooks against all files
uv pre-commit run --all-files
```

## License

- **Code:** MIT License (see [LICENSE](LICENSE))
- **Game Scenarios:** Creative Commons Attribution 4.0 International (CC BY 4.0) (see [scenarios/LICENSE](scenarios/LICENSE))

## Credits

- Inspired by the game [Reigns](https://www.devolverdigital.com/games/reigns)
- Built with [Flet](https://flet.dev/)