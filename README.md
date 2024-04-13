# PolySim

PolySim is a versatile simulation game built using the Flet framework, which allows you to write your application in Python and deploy it seamlessly across the web, Android, iOS, and desktop platforms. The simulator enable dynamic switching between game themes and mechanics via externally loaded JSON configuration files. The application is cross-platform and can run as a web app, desktop app, or on mobile devices.

## Features

- **Flet Framework Integration:** Build interactive UIs with Python for diverse platforms.
- **Modular Game Design:** Switch seamlessly between game themes like business management and space exploration.
- **Dynamic Configuration:** Game settings and rules are loaded dynamically from JSON files.
- **Extensible and Scalable:** Designed to easily incorporate additional themes and game mechanics.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Flet – a Python UI framework for building apps
- [Optional] Virtual environment (recommended)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/michaelborck/polysim.git
   ```
2. Navigate to the project directory:
   ```bash
   cd polysime
   ```
3. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Unix/macOS
   venv\Scripts\activate  # For Windows
   ```
4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Game

To start the game in a web browser, run the following command in the terminal:
```bash
flet main.py --web
```

To run as a desktop application:
```bash
flet main.py
```

## Usage

### Loading a Game Configuration

- From the main menu, select `Load Configuration`.
- Browse to and select the desired JSON configuration file.
- The game will initialize with the selected theme and settings.

### Example Configurations

Configuration files are located in the `configs/` directory:
- `business_management.json`: Configures the game for a business management scenario.
- `space_exploration.json`: Sets up a space exploration adventure.

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

Your Name - [@your_twitter](https://twitter.com/your_twitter) - email@example.com

Project Link: [https://github.com/yourusername/dynamic-game-simulator](https://github.com/yourusername/dynamic-game-simulator)

## Acknowledgments

- Thanks to everyone who has contributed to making this project possible.
- Special thanks to the Flet community for providing a versatile and powerful framework.
