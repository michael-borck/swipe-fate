# Technical Specification for "Reigns-like" Game in Flet

## Project Overview

This document outlines the technical specifications for creating a "Reigns-like" game using Flet, a framework for building cross-platform applications with Python. The game will be data-driven, with cards, resources, and visual assets defined in configuration files, enabling theming and customization.

## Core Requirements

### Game Mechanics
- Card-based gameplay similar to "Reigns"
- Data-driven approach with cards and game settings loaded from configuration files
- Resource management system affected by player decisions
- Left/right swipe or selection mechanic for decision making
- Mobile-first design approach with responsive UI for all device sizes

### Interface Components
- Title screen with options to:
  - Start new game
  - Load game configuration
  - Access settings
- Settings menu for:
  - Player name(s)
  - Difficulty levels (Easy, Standard, Hard)
  - Theme/visual filter selection
- Game screen displaying (in stacked order from top to bottom):
  - Resource indicators as icons with visual fill/shading (no numeric values)
  - Card text/story
  - Card image (centered)
  - Card title
  - Game stats section showing:
    - Player name
    - Turn counter (with configurable unit: hours, years, etc.)
    - Popularity/overall rating
    - Progress indicator (% complete)
  - Swipe/selection area for decisions

### Cross-Platform Support
- Desktop (Windows, macOS, Linux)
- Mobile (Android, iOS)
- Web
- Tablet

### Asset Management
- Default set of assets (card backs, resource icons, abstract card fronts)
- Support for custom assets loaded from configuration
- Asset handling for various platforms (local file system and URL-based loading)
- Optional image processing (scaling, grayscale, visual filters)

## Technical Architecture

### Technology Stack
- **Framework**: Flet 0.27+
- **Language**: Python 3.10+
- **Development Tools**:
  - uv for environment management
  - ruff for code formatting and linting
  - pytest for testing
  - mypy for type checking
  - Pydantic for data modeling and configuration parsing
  - MkDocs for documentation
- **Package Management**: pyproject.toml configuration
- **Distribution**: PyPI via twine 6.0.1
- **Version Control**: GitHub

### Module Structure

```
reigns_game/
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
├── .github/
│   └── workflows/
│       ├── tests.yml
│       └── publish.yml
├── docs/
│   ├── index.md
│   └── ...
├── tests/
│   ├── __init__.py
│   ├── test_game_logic.py
│   ├── test_config_loader.py
│   └── ...
├── reigns_game/
│   ├── __init__.py
│   ├── __main__.py
│   ├── assets/
│   │   ├── default/
│   │   │   ├── card_back.png
│   │   │   ├── resource_icons/
│   │   │   └── card_fronts/
│   │   └── themes/
│   ├── config/
│   │   ├── default_game.json
│   │   └── ...
│   ├── models/
│   │   ├── __init__.py
│   │   ├── card.py
│   │   ├── game_state.py
│   │   ├── resource.py
│   │   └── config.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── asset_manager.py
│   │   ├── config_loader.py
│   │   ├── game_logic.py
│   │   └── image_processor.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── app.py
│   │   ├── title_screen.py
│   │   ├── game_screen.py
│   │   ├── settings_screen.py
│   │   └── components/
│   │       ├── __init__.py
│   │       ├── card_display.py
│   │       ├── resource_bar.py
│   │       └── ...
│   ├── cli/
│   │   ├── __init__.py
│   │   └── cli_app.py
│   └── tui/
│       ├── __init__.py
│       └── tui_app.py
```

## Data Models

### Game Configuration Schema

```json
{
  "game_info": {
    "title": "Game Title",
    "description": "Game description",
    "version": "1.0.0",
    "author": "Author Name"
  },
  "theme": {
    "name": "Default Theme",
    "card_back": "path/to/card_back.png",
    "background": "path/to/background.png",
    "color_scheme": {
      "primary": "#4a4a4a",
      "secondary": "#f5f5f5",
      "accent": "#3273dc"
    },
    "resource_icons": {
      "resource1": "path/to/resource1_icon.png",
      "resource2": "path/to/resource2_icon.png"
    },
    "filters": {
      "default": "none",
      "available": ["grayscale", "cartoon", "oil_painting"]
    }
  },
  "game_settings": {
    "initial_resources": {
      "resource1": 50,
      "resource2": 50,
      "resource3": 50,
      "resource4": 50
    },
    "win_conditions": [
      {"resource": "resource1", "min": 10, "max": 90},
      {"resource": "resource2", "min": 10, "max": 90}
    ],
    "difficulty_modifiers": {
      "easy": 0.7,
      "standard": 1.0,
      "hard": 1.3
    },
    "turn_unit": "years",
    "stats": {
      "popularity_formula": "resource1*0.3 + resource2*0.4 - resource3*0.2 + resource4*0.1"
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
            "resource3": 10
          },
          "next_card": "card_003"
        }
      }
    }
  ]
}
```

### Core Pydantic Models

```python
# models/config.py
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, HttpUrl, field_validator, Field

class ResourceEffect(BaseModel):
    resource_id: str
    value: int

class CardChoice(BaseModel):
    text: str
    effects: Dict[str, int]
    next_card: Optional[str] = None

class Card(BaseModel):
    id: str
    title: str
    text: str
    image: Union[str, HttpUrl]
    choices: Dict[str, CardChoice]

class WinCondition(BaseModel):
    resource: str
    min: int
    max: int

class GameStats(BaseModel):
    popularity_formula: str = Field(default="resource1*0.4 + resource2*0.3 + resource3*0.2 + resource4*0.1")

class GameSettings(BaseModel):
    initial_resources: Dict[str, int]
    win_conditions: List[WinCondition]
    difficulty_modifiers: Dict[str, float]
    turn_unit: str = "years"
    stats: GameStats = Field(default_factory=GameStats)

class ColorScheme(BaseModel):
    primary: str
    secondary: str
    accent: str

class Theme(BaseModel):
    name: str
    card_back: Union[str, HttpUrl]
    background: Optional[Union[str, HttpUrl]] = None
    color_scheme: ColorScheme
    resource_icons: Dict[str, Union[str, HttpUrl]]
    filters: Dict[str, List[str]]

class GameInfo(BaseModel):
    title: str
    description: str
    version: str
    author: str

class GameConfig(BaseModel):
    game_info: GameInfo
    theme: Theme
    game_settings: GameSettings
    cards: List[Card]
```

## Key Components

### Asset Manager
- Handles loading of visual assets from both local filesystem and URLs
- Implements fallback mechanism for missing assets
- Manages asset caching for performance
- Handles image processing (scaling, filters)

### Config Loader
- Parses JSON configuration files using Pydantic models
- Validates configuration integrity
- Supports loading from local files and URLs
- Implements configuration merging (base + theme)

### Game Logic
- Manages game state including resources
- Processes card actions and their effects
- Handles win/lose conditions
- Implements difficulty modifiers
- Calculates popularity based on configurable formula
- Tracks game progress and completion percentage

### UI Components
- Card display with swipe/select interaction
- Resource indicators using visual fill/shading to show values
- Title screen with options
- Settings screens for configuration
- Mobile-first responsive design

## Implementation Details

### Game State Model

```python
# models/game_state.py
from typing import Dict, Set, Optional
from reigns_game.models.config import Card, GameSettings, Theme

class GameState:
    def __init__(
        self,
        resources: Dict[str, int],
        current_card: Card,
        settings: GameSettings,
        theme: Theme,
        difficulty: str = "standard",
        player_name: str = "Player"
    ):
        # Core game state
        self.resources = resources
        self.current_card = current_card
        self.settings = settings
        self.theme = theme
        
        # Game progress tracking
        self.turn_count = 0
        self.seen_cards: Set[str] = set()
        
        # Player settings
        self.difficulty = difficulty
        self.player_name = player_name
        
        # Additional state fields
        self.game_over = False
        self.end_message = ""
        
    @classmethod
    def new_game(cls, config, player_name: str = "Player", difficulty: str = "standard"):
        """Create a new game state from configuration"""
        # Initialize resources based on config
        resources = {
            resource_id: value 
            for resource_id, value in config.game_settings.initial_resources.items()
        }
        
        # Get first card (could be random or specific starting card)
        import random
        first_card = random.choice(config.cards)
        
        # Create new game state
        return cls(
            resources=resources,
            current_card=first_card,
            settings=config.game_settings,
            theme=config.theme,
            difficulty=difficulty,
            player_name=player_name
        )
        
    def save_game(self) -> dict:
        """Convert game state to a serializable dictionary for saving"""
        return {
            "resources": self.resources,
            "current_card_id": self.current_card.id,
            "turn_count": self.turn_count,
            "seen_cards": list(self.seen_cards),
            "difficulty": self.difficulty,
            "player_name": self.player_name,
            "game_over": self.game_over,
            "end_message": self.end_message
        }
    
    @classmethod
    def load_game(cls, save_data: dict, config):
        """Load game state from saved data and config"""
        # Find the current card by ID
        current_card = None
        for card in config.cards:
            if card.id == save_data["current_card_id"]:
                current_card = card
                break
        
        if not current_card:
            # Fallback if card not found
            import random
            current_card = random.choice(config.cards)
        
        # Create game state
        game_state = cls(
            resources=save_data["resources"],
            current_card=current_card,
            settings=config.game_settings,
            theme=config.theme,
            difficulty=save_data["difficulty"],
            player_name=save_data["player_name"]
        )
        
        # Restore additional state
        game_state.turn_count = save_data["turn_count"]
        game_state.seen_cards = set(save_data["seen_cards"])
        game_state.game_over = save_data["game_over"]
        game_state.end_message = save_data["end_message"]
        
        return game_state
```

### Game Logic Implementation

```python
# services/game_logic.py
from typing import Dict, List, Optional, Union, Any
import re
from reigns_game.models.game_state import GameState
from reigns_game.models.config import Card, GameConfig

class GameResult:
    def __init__(self, game_over: bool = False, message: str = ""):
        self.game_over = game_over
        self.message = message


class GameLogic:
    def __init__(self, game_state: GameState, config: GameConfig):
        self.game_state = game_state
        self.config = config
        # Set up the expression evaluator for popularity formula
        self.formula_pattern = re.compile(r'(resource\d+)')
    
    def process_choice(self, direction: str) -> GameResult:
        """Process player's choice (left or right)"""
        current_card = self.game_state.current_card
        
        if direction not in current_card.choices:
            return GameResult(False, "Invalid choice")
        
        choice = current_card.choices[direction]
        
        # Apply effects on resources based on difficulty
        difficulty_mod = self.game_state.settings.difficulty_modifiers[self.game_state.difficulty]
        
        for resource_id, value in choice.effects.items():
            if resource_id in self.game_state.resources:
                # Apply difficulty modifier
                modified_value = int(value * difficulty_mod)
                
                # Update resource value
                current_value = self.game_state.resources[resource_id]
                new_value = max(0, min(100, current_value + modified_value))
                self.game_state.resources[resource_id] = new_value
        
        # Increment turn counter
        self.game_state.turn_count += 1
        
        # Check for game over conditions
        game_over, message = self._check_game_over()
        if game_over:
            return GameResult(True, message)
        
        # Find next card
        if choice.next_card:
            self._set_next_card(choice.next_card)
        else:
            self._set_random_card()
            
        return GameResult(False)
    
    def calculate_popularity(self) -> int:
        """Calculate popularity based on the formula in config"""
        formula = self.config.game_settings.stats.popularity_formula
        
        # Replace resource references with actual values
        def replace_resource(match):
            resource_name = match.group(1)
            return str(self.game_state.resources.get(resource_name, 0))
        
        # Substitute resource placeholders with actual values
        formula_with_values = self.formula_pattern.sub(replace_resource, formula)
        
        try:
            # Evaluate the formula safely using restricted context
            result = eval(formula_with_values, {"__builtins__": {}})
            # Convert to percentage in 0-100 range
            popularity = max(0, min(100, int(result)))
            return popularity
        except Exception as e:
            print(f"Error evaluating popularity formula: {e}")
            # Default fallback - average of all resources
            if self.game_state.resources:
                return sum(self.game_state.resources.values()) // len(self.game_state.resources)
            return 50
    
    def calculate_progress(self) -> int:
        """Calculate game progress percentage"""
        # This could be based on different factors depending on game design
        # Options:
        # 1. Cards seen / total cards
        # 2. Turns / estimated total turns
        # 3. Story progression markers
        
        # For now, implement a basic version based on cards seen
        total_cards = len(self.config.cards)
        cards_seen = len(self.game_state.seen_cards)
        
        # Avoid division by zero
        if total_cards == 0:
            return 0
            
        progress = min(100, int((cards_seen / total_cards) * 100))
        return progress
    
    def _check_game_over(self) -> tuple[bool, str]:
        """Check if any game over conditions are met"""
        # Check resource-based win/lose conditions
        for condition in self.game_state.settings.win_conditions:
            resource_id = condition.resource
            if resource_id in self.game_state.resources:
                value = self.game_state.resources[resource_id]
                
                # Check if resource is outside allowed range
                if value < condition.min:
                    return True, f"Game over: {resource_id} too low!"
                if value > condition.max:
                    return True, f"Game over: {resource_id} too high!"
        
        # Could add other game over conditions here
        # - Turn limit reached
        # - Special ending card
        # - Achievement of specific goal
        
        return False, ""
    
    def _set_next_card(self, card_id: str) -> bool:
        """Set the specified card as the next one to display"""
        for card in self.config.cards:
            if card.id == card_id:
                self.game_state.current_card = card
                self.game_state.seen_cards.add(card_id)
                return True
                
        # If card not found, fall back to random
        self._set_random_card()
        return False
    
    def _set_random_card(self) -> None:
        """Set a random card from the deck as the next one"""
        import random
        
        # Filter out cards that require specific conditions
        available_cards = [card for card in self.config.cards 
                          if self._card_conditions_met(card)]
        
        if not available_cards:
            # If no cards available, reset seen cards and try again
            self.game_state.seen_cards.clear()
            available_cards = [card for card in self.config.cards 
                              if self._card_conditions_met(card)]
        
        if available_cards:
            next_card = random.choice(available_cards)
            self.game_state.current_card = next_card
            self.game_state.seen_cards.add(next_card.id)
        else:
            # This should never happen if there are cards in the config
            raise ValueError("No cards available to display")
    
    def _card_conditions_met(self, card: Card) -> bool:
        """Check if a card's conditions are met to be displayed"""
        # This could be expanded to check for prerequisites like:
        # - Resource levels
        # - Previous cards seen
        # - Turn number
        
        # For now, just avoid showing recently seen cards
        return card.id not in self.game_state.seen_cards
```

### Card Display Component

```python
# ui/components/card_display.py
import flet as ft
from reigns_game.models.config import Card

class CardDisplay(ft.GestureDetector):
    def __init__(
        self,
        card: Card,
        on_swipe_left=None,
        on_swipe_right=None,
        **kwargs
    ):
        self.card = card
        self.on_swipe_left = on_swipe_left
        self.on_swipe_right = on_swipe_right
        self.swipe_threshold = 50  # Minimum distance to count as a swipe
        self.is_swiping = False
        self.start_x = 0
        self.current_x = 0
        self.card_container = None
        self.card_image = None
        
        super().__init__(
            on_pan_start=self._on_pan_start,
            on_pan_update=self._on_pan_update,
            on_pan_end=self._on_pan_end,
            **kwargs
        )
    
    def build(self):
        # Responsive sizing
        container_width = min(350, self.page.width * 0.8 if self.page else 300)
        container_height = container_width * 1.5  # 3:2 aspect ratio
        
        # Card image
        self.card_image = ft.Image(
            src=self.card.image,
            width=container_width,
            height=container_height,
            fit=ft.ImageFit.COVER,
            border_radius=ft.border_radius.all(10),
        )
        
        # The card container that will be animated during swipe
        self.card_container = ft.Container(
            content=self.card_image,
            width=container_width,
            height=container_height,
            border_radius=ft.border_radius.all(10),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.colors.BLACK26,
                offset=ft.Offset(2, 2)
            ),
            animate=ft.animation.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
            alignment=ft.alignment.center
        )
        
        # Center the card in the container
        return ft.Container(
            content=self.card_container,
            width=container_width,
            height=container_height,
            alignment=ft.alignment.center
        )
    
    def _on_pan_start(self, e: ft.DragStartEvent):
        """Handle the start of a swipe gesture"""
        self.is_swiping = True
        self.start_x = e.local_x
        self.current_x = e.local_x
    
    def _on_pan_update(self, e: ft.DragUpdateEvent):
        """Handle ongoing swipe gesture updates"""
        if not self.is_swiping:
            return
            
        self.current_x = e.local_x
        delta_x = self.current_x - self.start_x
        
        # Limit the drag distance
        max_drag = 100
        if abs(delta_x) > max_drag:
            delta_x = max_drag if delta_x > 0 else -max_drag
        
        # Update the card position
        self.card_container.offset = ft.transform.Offset(delta_x / 100, 0)
        
        # Add rotation based on the drag distance
        angle = (delta_x / 100) * 0.2  # Reduce rotation amount
        self.card_container.rotate = ft.transform.Rotate(angle)
        
        # Add opacity change to indicate the swipe direction
        if delta_x > 20:  # Right swipe - positive choice
            self.card_container.border = ft.border.all(2, ft.colors.GREEN)
        elif delta_x < -20:  # Left swipe - negative choice
            self.card_container.border = ft.border.all(2, ft.colors.RED)
        else:
            self.card_container.border = None
            
        self.update()
    
    def _on_pan_end(self, e: ft.DragEndEvent):
        """Handle the end of a swipe gesture"""
        if not self.is_swiping:
            return
            
        self.is_swiping = False
        delta_x = self.current_x - self.start_x
        
        # Reset the card position with animation
        self.card_container.offset = ft.transform.Offset(0, 0)
        self.card_container.rotate = ft.transform.Rotate(0)
        self.card_container.border = None
        self.update()
        
        # Check if the swipe was decisive enough
        if abs(delta_x) > self.swipe_threshold:
            if delta_x > 0 and self.on_swipe_right:
                self.on_swipe_right(e)
            elif delta_x < 0 and self.on_swipe_left:
                self.on_swipe_left(e)
    
    def update_card(self, card: Card):
        """Update the card being displayed"""
        self.card = card
        # Update the image
        self.card_image.src = card.image
        # Force update
        self.update()
```

### Game Screen Implementation

```python
# ui/game_screen.py
import flet as ft
from reigns_game.models.game_state import GameState
from reigns_game.services.game_logic import GameLogic
from reigns_game.ui.components.card_display import CardDisplay

class GameScreen(ft.UserControl):
    def __init__(self, game_state: GameState, game_logic: GameLogic):
        super().__init__()
        self.game_state = game_state
        self.game_logic = game_logic
        self.card_display = None
        self.resource_icons = {}
        
    def build(self):
        # Responsive layout for mobile-first design
        # Calculate if we're on a small screen
        is_mobile = self.page.width < 600 if self.page and self.page.width else True
        
        # Create resource icons with visual fill indicators
        resource_container = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                self._create_resource_icon(resource_id, data)
                for resource_id, data in self.game_state.resources.items()
            ]
        )
        
        # Create card components
        card_text = ft.Container(
            content=ft.Text(
                self.game_state.current_card.text,
                size=16 if is_mobile else 18,
                text_align=ft.TextAlign.CENTER
            ),
            margin=ft.margin.only(bottom=10, top=10),
            padding=ft.padding.all(10)
        )
        
        # Create card display
        self.card_display = CardDisplay(
            self.game_state.current_card,
            on_swipe_left=self._handle_swipe_left,
            on_swipe_right=self._handle_swipe_right
        )
        
        card_title = ft.Text(
            self.game_state.current_card.title,
            size=20 if is_mobile else 24,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        )
        
        # Game stats section
        game_stats = self._create_game_stats()
        
        # Decision buttons
        decision_buttons = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            controls=[
                ft.ElevatedButton(
                    text=self.game_state.current_card.choices["left"].text,
                    on_click=self._handle_swipe_left,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10)
                    )
                ),
                ft.ElevatedButton(
                    text=self.game_state.current_card.choices["right"].text,
                    on_click=self._handle_swipe_right,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10)
                    )
                ),
            ]
        )

        # Stack all components in the required order
        return ft.Column(
            controls=[
                resource_container,
                card_text,
                self.card_display,
                card_title,
                game_stats,
                decision_buttons
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10,
            expand=True
        )

    def _create_resource_icon(self, resource_id, data):
        # Create a resource icon with visual fill indicator (no text)
        # Get the base icon image
        icon_path = self.game_state.theme.resource_icons[resource_id]
        
        # Create a container to hold the icon with a visual fill indicator
        # This will be a stack with two versions of the icon - filled and unfilled
        # The filled portion will be clipped based on the resource amount
        
        # The filled (colored) version
        filled_icon = ft.Image(
            src=icon_path,
            width=50,
            height=50,
            fit=ft.ImageFit.CONTAIN
        )
        
        # The unfilled (greyed out) version - positioned at the top
        # and clipped based on resource value
        unfilled_icon = ft.Container(
            content=ft.Image(
                src=icon_path,
                width=50,
                height=50,
                color=ft.colors.GREY_400,
                opacity=0.5,
                fit=ft.ImageFit.CONTAIN
            ),
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            # Clip from the bottom based on the resource value
            height=(100 - data) / 100 * 50,
            alignment=ft.alignment.top_center
        )
        
        icon_container = ft.Stack(
            controls=[
                filled_icon,
                unfilled_icon
            ],
            width=50,
            height=50
        )
        
        self.resource_icons[resource_id] = icon_container
        return icon_container
        
    def _create_game_stats(self):
        # Calculate popularity based on the formula in game settings
        popularity = self.game_logic.calculate_popularity()
        
        # Format turn count with the appropriate unit
        turn_text = f"{self.game_state.turn_count} {self.game_state.settings.turn_unit}"
        
        # Calculate progress percentage - this could be based on turns, cards seen, etc.
        progress = self.game_logic.calculate_progress()
        
        # Create the stats container
        stats_container = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(f"Player: {self.game_state.player_name}", size=14),
                    ft.Text(f"Turns: {turn_text}", size=14)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([
                    ft.Text(f"Popularity: {popularity}%", size=14),
                    ft.Text(f"Progress: {progress}%", size=14)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ]),
            padding=10,
            border_radius=5,
            bgcolor=ft.colors.BLACK12
        )
        
        return stats_container
    
    def _handle_swipe_left(self, e):
        """Process the left swipe action"""
        self._process_choice("left")

    def _handle_swipe_right(self, e):
        """Process the right swipe action"""
        self._process_choice("right")

    def _process_choice(self, direction):
        # Process the choice using game logic
        result = self.game_logic.process_choice(direction)
        
        # Update UI components
        for resource_id, value in self.game_state.resources.items():
            # Update the resource icon fill level
            if resource_id in self.resource_icons:
                stack = self.resource_icons[resource_id]
                # Update the unfilled (greyed out) portion height
                unfilled_container = stack.controls[1]
                unfilled_container.height = (100 - value) / 100 * 50
                stack.update()
        
        # Update card display with the new card
        self.card_display.update_card(self.game_state.current_card)
        
        # Update card text and title
        for control in self.controls[0].controls:
            if isinstance(control, ft.Container) and hasattr(control, "content") and isinstance(control.content, ft.Text):
                # This is the card text container
                control.content.value = self.game_state.current_card.text
                control.update()
            elif isinstance(control, ft.Text) and control != self.controls[0].controls[0]:
                # This is the card title
                control.value = self.game_state.current_card.title
                control.update()
        
        # Update game stats
        for i, control in enumerate(self.controls[0].controls):
            if i == 4:  # Game stats is the 5th control (index 4)
                new_stats = self._create_game_stats()
                self.controls[0].controls[i] = new_stats
                self.update()
                break
        
        # Check for game over condition
        if result.game_over:
            self.page.dialog = ft.AlertDialog(
                title=ft.Text("Game Over"),
                content=ft.Text(result.message),
                actions=[
                    ft.TextButton("New Game", on_click=self._new_game),
                    ft.TextButton("Main Menu", on_click=self._main_menu)
                ]
            )
            self.page.dialog.open = True
            self.page.update()
    
    def _new_game(self, e):
        """Start a new game with the same settings"""
        # This would typically navigate back to the parent app
        # which would then create a new game state
        pass
    
    def _main_menu(self, e):
        """Return to the main menu"""
        # This would typically navigate back to the title screen
        pass
```

### Asset Manager Implementation

```python
# services/asset_manager.py
import os
import aiohttp
import asyncio
from pathlib import Path
from typing import Dict, Optional, Union
from PIL import Image, ImageFilter, ImageOps

class AssetManager:
    def __init__(self, base_path: str, default_assets_path: str):
        self.base_path = Path(base_path)
        self.default_assets_path = Path(default_assets_path)
        self.cache: Dict[str, Union[str, bytes]] = {}
        
    async def get_image(self, image_path: str, filter_type: Optional[str] = None) -> str:
        """Load an image from filesystem or URL, apply filters if specified, and return path for Flet to use"""
        cache_key = f"{image_path}_{filter_type if filter_type else 'none'}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        try:
            # Try to load from local path first
            path = Path(image_path)
            if path.is_absolute():
                img_path = path
            else:
                img_path = self.base_path / image_path
                
            if not img_path.exists():
                # Try to load from URL if it looks like a URL
                if image_path.startswith(('http://', 'https://')):
                    temp_path = await self._download_image(image_path)
                    img_path = temp_path
                else:
                    # Fall back to default asset
                    default_img = self._get_default_asset_for_type(image_path)
                    img_path = self.default_assets_path / default_img
            
            # Apply filters if needed
            if filter_type:
                filtered_path = await self._apply_filter(img_path, filter_type)
                self.cache[cache_key] = str(filtered_path)
                return str(filtered_path)
            
            self.cache[cache_key] = str(img_path)
            return str(img_path)
            
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            # Return a default fallback image
            fallback = self.default_assets_path / "card_back.png"
            self.cache[cache_key] = str(fallback)
            return str(fallback)
    
    async def _download_image(self, url: str) -> Path:
        """Download image from URL and save to temp location"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.read()
                    # Create a temp file path
                    temp_dir = Path.home() / ".reigns_game" / "cache"
                    temp_dir.mkdir(parents=True, exist_ok=True)
                    
                    filename = url.split("/")[-1]
                    temp_path = temp_dir / filename
                    
                    with open(temp_path, "wb") as f:
                        f.write(content)
                    
                    return temp_path
                else:
                    raise Exception(f"Failed to download {url}, status {response.status}")
    
    async def _apply_filter(self, img_path: Path, filter_type: str) -> Path:
        """Apply a filter to an image and save the result"""
        img = Image.open(img_path)
        
        if filter_type == "grayscale":
            filtered = ImageOps.grayscale(img)
        elif filter_type == "cartoon":
            # Simple cartoon effect
            filtered = img.filter(ImageFilter.CONTOUR)
            filtered = filtered.filter(ImageFilter.SMOOTH)
        elif filter_type == "oil_painting":
            # Simple oil painting effect
            filtered = img.filter(ImageFilter.SMOOTH_MORE)
            filtered = filtered.filter(ImageFilter.EDGE_ENHANCE)
        else:
            # No recognized filter, return original
            return img_path
        
        # Save the filtered image
        output_dir = Path.home() / ".reigns_game" / "filtered"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / f"{img_path.stem}_{filter_type}{img_path.suffix}"
        filtered.save(output_path)
        return output_path
    
    def _get_default_asset_for_type(self, path: str) -> str:
        """Return appropriate default asset based on the path/type"""
        if "card_back" in path:
            return "default/card_back.png"
        elif "resource" in path:
            # Determine which resource based on name or position
            resource_num = 1  # Default
            if "resource" in path:
                try:
                    resource_num = int(path.split("resource")[1][0])
                except:
                    pass
            return f"default/resource_icons/resource{resource_num}.png"
        else:
            # Default to a card front
            return "default/card_fronts/card1.png"
```

### Config Loader Implementation

```python
# services/config_loader.py
import json
from pathlib import Path
import aiohttp
from typing import Union, Dict, Any, Optional
from reigns_game.models.config import GameConfig

class ConfigLoader:
    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        
    async def load_config(self, config_path: str) -> GameConfig:
        """Load game configuration from file path or URL"""
        try:
            # Check if it's a URL
            if config_path.startswith(('http://', 'https://')):
                config_data = await self._load_from_url(config_path)
            else:
                # Try as relative path, then absolute
                if not Path(config_path).is_absolute():
                    file_path = self.base_path / config_path
                else:
                    file_path = Path(config_path)
                    
                config_data = self._load_from_file(file_path)
            
            # Parse using Pydantic for validation
            return GameConfig.model_validate(config_data)
            
        except Exception as e:
            print(f"Error loading config: {e}")
            # Load default config as fallback
            default_path = Path(__file__).parent.parent / "config" / "default_game.json"
            default_data = self._load_from_file(default_path)
            return GameConfig.model_validate(default_data)
    
    def _load_from_file(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration from a local file"""
        if not file_path.exists():
            raise FileNotFoundError(f"Config file not found: {file_path}")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    async def _load_from_url(self, url: str) -> Dict[str, Any]:
        """Load configuration from a URL"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Failed to download config from {url}, status {response.status}")
    
    async def merge_configs(self, base_config: GameConfig, override_config: Dict[str, Any]) -> GameConfig:
        """Merge a base config with override values"""
        # Convert base config to dict
        base_dict = base_config.model_dump()
        
        # Deep merge the dictionaries
        merged = self._deep_merge(base_dict, override_config)
        
        # Validate and return new config
        return GameConfig.model_validate(merged)
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries"""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
                
        return result
```

### Mobile-First Responsive Layout

```python
# ui/app.py
import flet as ft
from reigns_game.models.game_state import GameState
from reigns_game.services.game_logic import GameLogic
from reigns_game.services.config_loader import ConfigLoader
from reigns_game.services.asset_manager import AssetManager
from reigns_game.ui.title_screen import TitleScreen
from reigns_game.ui.game_screen import GameScreen
from reigns_game.ui.settings_screen import SettingsScreen


class ReignsApp(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.config_loader = ConfigLoader()
        self.asset_manager = AssetManager(
            base_path=".",
            default_assets_path="./reigns_game/assets/default"
        )
        self.game_state = None
        self.game_logic = None
        self.current_screen = None
        
        # Configure the page
        self._configure_page()
    
    def _configure_page(self):
        """Configure the page settings"""
        self.page.title = "Reigns Game"
        self.page.theme_mode = ft.ThemeMode.SYSTEM
        self.page.padding = 0
        self.page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.page.on_resize = self._handle_resize
        
        # Set up responsive design
        self.is_mobile = self.page.width is not None and self.page.width < 600
        self.page.on_window_event = self._handle_window_event
        
        # Add a loading indicator
        self.loading = ft.ProgressRing()
        self.loading.visible = False
        self.page.overlay.append(self.loading)
    
    def _handle_resize(self, e):
        """Handle page resize events"""
        # Update responsive layout flag
        self.is_mobile = self.page.width < 600
        
        # Update the current screen if it exists
        if self.current_screen:
            self.current_screen.update()
    
    def _handle_window_event(self, e):
        """Handle window events like focus/blur"""
        if e.data == "focus":
            # Could resume game, reload assets, etc.
            pass
        elif e.data == "blur":
            # Could pause game, save state, etc.
            pass
    
    async def load_config(self, config_path: str):
        """Load a game configuration"""
        self.loading.visible = True
        self.page.update()
        
        try:
            config = await self.config_loader.load_config(config_path)
            self.game_state = GameState.new_game(config)
            self.game_logic = GameLogic(self.game_state, config)
            
            # Preload assets in background
            await self._preload_assets()
            
            return True
        except Exception as e:
            print(f"Error loading config: {e}")
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error loading game: {str(e)}"),
                action="OK"
            )
            self.page.snack_bar.open = True
            self.page.update()
            return False
        finally:
            self.loading.visible = False
            self.page.update()
    
    async def _preload_assets(self):
        """Preload commonly used assets"""
        if not self.game_state:
            return
            
        # Preload card back
        await self.asset_manager.get_image(self.game_state.theme.card_back)
        
        # Preload resource icons
        for icon_path in self.game_state.theme.resource_icons.values():
            await self.asset_manager.get_image(icon_path)
    
    def navigate_to(self, screen_name: str, **kwargs):
        """Navigate to a specific screen"""
        if screen_name == "title":
            self.current_screen = TitleScreen(
                on_start_game=lambda: self.navigate_to("game"),
                on_load_config=self._handle_load_config,
                on_settings=lambda: self.navigate_to("settings")
            )
        elif screen_name == "game":
            if not self.game_state:
                # Create a new game with default config if none exists
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text("Loading default game configuration..."),
                    action="OK"
                )
                self.page.snack_bar.open = True
                self.page.update()
                
                default_config_path = "./reigns_game/config/default_game.json"
                success = await self.load_config(default_config_path)
                if not success:
                    self.navigate_to("title")
                    return
            
            self.current_screen = GameScreen(
                game_state=self.game_state,
                game_logic=self.game_logic
            )
        elif screen_name == "settings":
            self.current_screen = SettingsScreen(
                on_save=self._handle_save_settings,
                on_cancel=lambda: self.navigate_to("title"),
                settings=self._get_current_settings()
            )
        else:
            # Default to title screen
            self.current_screen = TitleScreen(
                on_start_game=lambda: self.navigate_to("game"),
                on_load_config=self._handle_load_config,
                on_settings=lambda: self.navigate_to("settings")
            )
        
        # Update the UI
        self.page.controls.clear()
        self.page.controls.append(self.current_screen)
        self.page.update()
    
    async def _handle_load_config(self, config_path: str):
        """Handle loading a new configuration"""
        success = await self.load_config(config_path)
        if success:
            self.navigate_to("game")
    
    def _handle_save_settings(self, settings: dict):
        """Handle saving settings"""
        if self.game_state:
            self.game_state.player_name = settings.get("player_name", "Player")
            self.game_state.difficulty = settings.get("difficulty", "standard")
            
            # Apply theme/filter changes if needed
            filter_type = settings.get("filter")
            if filter_type and filter_type != "none":
                # Update assets with the new filter
                pass
        
        self.navigate_to("title")
    
    def _get_current_settings(self) -> dict:
        """Get current settings for the settings screen"""
        if not self.game_state:
            return {
                "player_name": "Player",
                "difficulty": "standard",
                "filter": "none"
            }
        
        return {
            "player_name": self.game_state.player_name,
            "difficulty": self.game_state.difficulty,
            "filter": "none"  # Currently active filter
        }
    
    def build(self):
        # Start with the title screen
        self.navigate_to("title")
        
        # Container that fills the page
        return ft.Container(
            expand=True,
            content=self.current_screen
        )


def main(page: ft.Page):
    app = ReignsApp(page)
    page.add(app)
```

## Testing Strategy

### Unit Tests

```python
# tests/test_config_loader.py
import pytest
import json
from pathlib import Path
from reigns_game.services.config_loader import ConfigLoader
from reigns_game.models.config import GameConfig

@pytest.fixture
def sample_config():
    return {
        "game_info": {
            "title": "Test Game",
            "description": "Test game description",
            "version": "1.0.0",
            "author": "Test Author"
        },
        "theme": {
            "name": "Test Theme",
            "card_back": "card_back.png",
            "color_scheme": {
                "primary": "#000000",
                "secondary": "#ffffff",
                "accent": "#ff0000"
            },
            "resource_icons": {
                "resource1": "resource1.png",
                "resource2": "resource2.png"
            },
            "filters": {
                "default": "none",
                "available": ["grayscale"]
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
            },
            "turn_unit": "years",
            "stats": {
                "popularity_formula": "resource1*0.5 + resource2*0.5"
            }
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
                        "effects": {
                            "resource1": 10
                        },
                        "next_card": "card_002"
                    },
                    "right": {
                        "text": "Right choice",
                        "effects": {
                            "resource2": -5
                        }
                    }
                }
            }
        ]
    }

@pytest.fixture
def config_file(sample_config, tmp_path):
    config_path = tmp_path / "test_config.json"
    with open(config_path, 'w') as f:
        json.dump(sample_config, f)
    return config_path

@pytest.mark.asyncio
async def test_load_config_from_file(config_file):
    # Arrange
    loader = ConfigLoader(str(config_file.parent))
    
    # Act
    config = await loader.load_config(config_file.name)
    
    # Assert
    assert isinstance(config, GameConfig)
    assert config.game_info.title == "Test Game"
    assert len(config.cards) == 1
    assert config.cards[0].id == "card_001"
    assert config.game_settings.turn_unit == "years"
```

### Testing Game Logic

```python
# tests/test_game_logic.py
import pytest
from reigns_game.models.game_state import GameState
from reigns_game.models.config import GameConfig
from reigns_game.services.game_logic import GameLogic

@pytest.fixture
def sample_config():
    # Create a minimal config for testing
    return GameConfig.model_validate({
        "game_info": {
            "title": "Test Game",
            "description": "Test game description",
            "version": "1.0.0",
            "author": "Test Author"
        },
        "theme": {
            "name": "Test Theme",
            "card_back": "card_back.png",
            "color_scheme": {
                "primary": "#000000",
                "secondary": "#ffffff",
                "accent": "#ff0000"
            },
            "resource_icons": {
                "resource1": "resource1.png",
                "resource2": "resource2.png"
            },
            "filters": {
                "default": "none",
                "available": ["grayscale"]
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
            },
            "turn_unit": "years",
            "stats": {
                "popularity_formula": "resource1*0.5 + resource2*0.5"
            }
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
                        "effects": {
                            "resource1": 10
                        },
                        "next_card": "card_002"
                    },
                    "right": {
                        "text": "Right choice",
                        "effects": {
                            "resource2": -5
                        }
                    }
                }
            },
            {
                "id": "card_002",
                "title": "Test Card 2",
                "text": "Test card text 2",
                "image": "card2.png",
                "choices": {
                    "left": {
                        "text": "Left choice",
                        "effects": {
                            "resource1": -5
                        }
                    },
                    "right": {
                        "text": "Right choice",
                        "effects": {
                            "resource2": 10
                        }
                    }
                }
            }
        ]
    })

def test_process_choice_left(sample_config):
    # Arrange
    game_state = GameState.new_game(sample_config)
    game_logic = GameLogic(game_state, sample_config)
    
    # Act
    result = game_logic.process_choice("left")
    
    # Assert
    assert result.game_over == False
    assert game_state.resources["resource1"] == 60  # 50 + 10
    assert game_state.turn_count == 1
    assert game_state.current_card.id == "card_002"

def test_process_choice_right(sample_config):
    # Arrange
    game_state = GameState.new_game(sample_config)
    game_logic = GameLogic(game_state, sample_config)
    
    # Act
    result = game_logic.process_choice("right")
    
    # Assert
    assert result.game_over == False
    assert game_state.resources["resource2"] == 45  # 50 - 5
    assert game_state.turn_count == 1

def test_game_over_condition(sample_config):
    # Arrange
    game_state = GameState.new_game(sample_config)
    game_logic = GameLogic(game_state, sample_config)
    
    # Manipulate resources to trigger game over
    game_state.resources["resource1"] = 85
    
    # Act
    result = game_logic.process_choice("left")
    
    # Assert
    assert result.game_over == True
    assert "too high" in result.message.lower()

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
```

## Distribution and Packaging

### pyproject.toml Configuration

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "reigns_game"
version = "0.1.0"
description = "A data-driven card-based decision game inspired by Reigns"
readme = "README.md"
requires-python = ">=3.10"
license = { text = "MIT" }
authors = [
    { name = "Your Name", email = "your.email@example.com" }
]
dependencies = [
    "flet>=0.27.0",
    "pillow>=9.0.0",
    "pydantic>=2.0.0",
    "aiohttp>=3.8.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.18.0",
    "mypy>=1.0.0",
    "ruff>=0.0.230",
    "mkdocs>=1.3.0",
    "mkdocs-material>=8.2.0",
]

[project.scripts]
reigns-game = "reigns_game.__main__:main"

[tool.ruff]
line-length = 88
target-version = "py310"
select = ["E", "F", "I"]

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
```

## Development Workflow

1. Setup environment with uv:
   ```bash
   uv venv
   uv pip install -e ".[dev]"
   ```

2. Run formatting and linting:
   ```bash
   ruff format .
   ruff check .
   ```

3. Run type checking:
   ```bash
   mypy reigns_game
   ```

4. Run tests:
   ```bash
   pytest
   ```

5. Build documentation:
   ```bash
   mkdocs build
   ```

6. Package and publish:
   ```bash
   python -m build
   twine upload dist/*
   ```

## Implementation Plan

### Phase 1: Core Framework
- Setup project structure and dependencies
- Implement data models and config loading
- Create basic asset management system
- Design core game logic system

### Phase 2: Basic UI Implementation
- Build title screen UI with mobile-first design
- Implement game screen with resource indicators and card display
- Create settings screen with player preferences
- Implement mobile-responsive layouts

### Phase 3: Game Logic and Asset Management
- Complete card interactions and resource effects
- Implement win/lose conditions
- Enhance asset management with fallbacks
- Add image filtering capabilities
- Implement progress tracking and statistics

### Phase 4: Optional Features
- Implement CLI version (if time permits)
- Implement TUI version (if time permits)
- Add save/load game functionality
- Enhance theming capabilities

### Phase 5: Testing and Documentation
- Complete unit and integration tests
- Finalize documentation
- Create example game configurations
- Package and publish to PyPI

## Deliverables

1. Complete source code on GitHub
2. PyPI package for easy installation
3. Documentation with:
   - Installation guide
   - Developer documentation
   - Configuration guide
   - Example game configs
4. Example themes and game presets

This technical specification provides a comprehensive roadmap for implementing a "Reigns-like" game using Flet with a mobile-first design approach. The implementation details cover all the required features while maintaining a clean architecture that separates concerns into models, services, and UI components.