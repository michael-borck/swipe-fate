# SwipeFate

SwipeFate is a versatile simulation game built using the Flet framework, which allows you to write your application in Python and deploy it seamlessly across the web, Android, iOS, and desktop platforms. The simulator enable dynamic switching between game themes and mechanics via externally loaded JSON configuration files. The application is cross-platform and can run as a web app, desktop app, or on mobile devices.

## Features

- **Flet Framework Integration:** Build interactive UIs with Python for diverse platforms.
- **Modular Game Design:** Switch seamlessly between game themes like business management and space exploration.
- **Dynamic Configuration:** Game settings and rules are loaded dynamically from JSON files.
- **Extensible and Scalable:** Designed to easily incorporate additional themes and game mechanics.

## Project Structure

```
SwipeFate/
├── src/                   # Source code directory
│   └── swipe_fate/        # Main package
│       ├── core/         # Core game engine components
│       │   ├── core_engine.py
│       │   ├── game_state.py
│       │   ├── event.py
│       │   └── ...
│       ├── ui/           # User interface components
│       │   └── ui_manager.py
│       ├── resource_loader.py
│       └── main.py       # Application entry point
├── configs/              # Game configuration files
│   ├── business.json
│   └── space_exploration.json
├── assets/               # Game assets (images, sounds, etc.)
├── tests/                # Test directory
├── pyproject.toml        # Modern Python project configuration
└── run_swipe_fate.py     # Convenience script for running the game
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Flet – a Python UI framework for building apps
- [Optional] Virtual environment (recommended)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/michaelborck/SwipeFate.git
   ```
2. Navigate to the project directory:
   ```bash
   cd SwipeFatee
   ```
3. Create a virtual environment with uv (recommended):
   ```bash
   uv venv
   source .venv/bin/activate  # For Unix/macOS
   .venv\Scripts\activate  # For Windows
   ```
4. Install the package and dependencies:
   ```bash
   uv pip install -e ".[dev]"
   ```

### Running the Game

To start the game in a web browser, run the following command in the terminal:
```bash
# Using the convenience script
./run_swipe_fate.py --web

# Or using flet directly
flet src/swipe_fate/main.py --web
```

To run as a desktop application:
```bash
# Using the convenience script
./run_swipe_fate.py

# Or using flet directly
flet src/swipe_fate/main.py
```

### Development Tools

SwipeFate uses modern Python development tools:

- **ruff**: For linting and formatting
  ```bash
  ruff check .
  ruff format .
  ```

- **mypy**: For type checking
  ```bash
  mypy src
  ```

- **pytest**: For testing
  ```bash
  pytest
  pytest --cov=swipe_fate
  ```

## Usage

### Loading a Game Configuration

- From the main menu, select `Load Configuration`.
- Browse to and select the desired JSON configuration file.
- The game will initialize with the selected theme and settings.

### Example Configurations

Configuration files are located in the `configs/` directory:
- `business.json`: Configures the game for a business management scenario.
- `space_exploration.json`: Sets up a space exploration adventure.

## Documentation

Comprehensive documentation is available in the [docs/](docs/) directory:

- [Technical Documentation](docs/technical.md) - System architecture and implementation
- [Design Document](docs/design.md) - Game concept and design principles
- [Game Configuration Guide](docs/game-config.md) - Creating your own game themes
- [Development Roadmap](docs/roadmap.md) - Planned features and priorities

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact


## Acknowledgments

- Thanks to everyone who has contributed to making this project possible.
- Special thanks to the Flet community for providing a versatile and powerful framework.
