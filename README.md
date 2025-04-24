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
- **Customizable themes** (Selectable via Settings)

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/swipe-verse.git
cd swipe-verse

# Install with pip (preferably in a virtual environment)
pip install -e .
```

## Usage

To run the game locally during development:

```bash
# Run the Flet app 
# (defaults to the tutorial game)
flet run swipe_verse/main.py 

# Or, if installed via pip install -e .:
swipe-verse 
```

Game scenarios can be changed from the in-app Settings menu.

## Building for Distribution

Use the standard Flet build commands:

```bash
# Build for Web
flet build web

# Build for macOS (run on macOS)
flet build macos

# Build for Windows (run on Windows)
flet build windows --platform amd64  # or arm64

# Build for Linux (run on Linux)
flet build linux

# Build for Android (requires Android SDK/toolchain setup)
flet build apk 
# or flet build aab

# Build for iOS (requires macOS and Xcode setup)
flet build ios
```

See the [Flet deployment documentation](https://flet.dev/docs/guides/python/deploying-app) for more details on prerequisites for each platform.

## Game Scenarios

The game is data-driven using JSON scenario files located in `swipe_verse/scenarios/`:

- `kingdom_game.json` - Medieval kingdom management
- `business_game.json` - Corporate leadership simulation
- `tutorial_game.json` - Interactive guide to gameplay mechanics

### Example Configuration Snippet (`kingdom_game.json`)

```json
{
  "game_info": {
    "title": "Kingdom Fate",
    "description": "Rule your medieval kingdom through the power of swiping",
    "version": "0.1.0",
    // ...
  },
  "theme": {
    "name": "Kingdom Theme",
    "resource_icons": {
      "treasury": "swipe_verse/assets/themes/medieval/resource_icons/treasury.png",
      "population": "swipe_verse/assets/themes/medieval/resource_icons/population.png",
      "military": "swipe_verse/assets/themes/medieval/resource_icons/military.png",
      "church": "swipe_verse/assets/themes/medieval/resource_icons/church.png"
    },
    // ...
  },
  "game_settings": {
    "initial_resources": {
      "treasury": 50,
      "population": 50,
      "military": 50,
      "church": 50
    },
    // ...
  },
  "cards": [
    {
      "id": "card_001",
      "title": "The Harvest",
      "text": "This year's harvest is meager...",
      "image": "swipe_verse/assets/themes/medieval/card_fronts/harvest.png",
      "choices": {
        "left": {
          "text": "Raise taxes",
          "effects": { "treasury": 15, "population": -10, "church": -5 },
          "next_card": "card_002"
        },
        "right": {
          "text": "Distribute grain",
          "effects": { "treasury": -10, "population": 15, "military": 5 },
          "next_card": "card_003"
        }
      }
    }
    // ...
  ]
}
```
*(Note: Asset paths in JSON should be relative to the project root, e.g., `swipe_verse/assets/...`)*

## Development

This project uses:
- [Flet](https://flet.dev/) for UI
- [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation (consider adding if needed for config loading)
- [Ruff](https://github.com/charliermarsh/ruff) for linting
- [mypy](http://mypy-lang.org/) for type checking
- [pytest](https://docs.pytest.org/) for testing

### Development Setup

```bash
# Install dev dependencies (using uv or pip)
# uv pip install -e ".[dev]" 
pip install -e ".[dev]"

# Run linting
ruff check .

# Run type checking
mypy swipe_verse

# Run tests
pytest
```

### Development Tools

The `tools/` directory contains some diagnostic utilities:

```bash
# Run diagnostic tests for Flet environment
python tools/test_flet_module.py 
```

The custom build script (`tools/build.py`) has been removed in favor of standard `flet build` commands.

### Pre-commit Hooks

Use pre-commit to automatically format, lint, and type-check code before commits.

```bash
# Install pre-commit into your environment
# uv pip install pre-commit
pip install pre-commit

# Install Git hook scripts
# uv pre-commit install
pre-commit install

# Run all hooks against all files
# uv pre-commit run --all-files
pre-commit run --all-files
```

## License

- **Code:** MIT License (see [LICENSE](LICENSE))
- **Game Scenarios:** Creative Commons Attribution 4.0 International (CC BY 4.0) (see [scenarios/LICENSE](scenarios/LICENSE))

## Credits

- Inspired by the game [Reigns](https://www.devolverdigital.com/games/reigns)
- Built with [Flet](https://flet.dev/)
