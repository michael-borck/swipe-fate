# SwipeFate Technical Documentation

## Architecture Overview

SwipeFate follows a component-based architecture with an event-driven design pattern. The main components are:

- **Core Engine**: Central coordinator that manages game state and systems
- **Game State**: Maintains the current state of resources and entities
- **Event System**: Allows communication between components via events
- **Resource Loader**: Loads game configurations from JSON files
- **UI Manager**: Handles the user interface components and interactions

## Component Relationships

```
┌─────────────┐     ┌─────────────┐
│ Core Engine │────▶│ Game State  │
└─────────────┘     └─────────────┘
      │ ▲                 │
      │ │                 │
      ▼ │                 ▼
┌─────────────┐     ┌─────────────┐
│Event Manager│◀───▶│ Rule Engine │
└─────────────┘     └─────────────┘
      │ ▲
      │ │
      ▼ │
┌─────────────┐     ┌─────────────┐
│ UI Manager  │◀───▶│   Resource  │
└─────────────┘     │   Loader    │
                    └─────────────┘
```

## File Structure

- **main.py**: Application entry point
- **core/**: Core engine and game state management
  - **core_engine.py**: Main game loop and coordination
  - **game_state.py**: State management
  - **event.py**: Event data structure
  - **event_manager.py**: Event subscription and dispatch
  - **rule_engine.py**: Rules processing
  - **component_system.py**: Entity-component system
- **ui/**: User interface components
  - **ui_manager.py**: UI coordination and rendering
- **resource_loader.py**: Configuration loading

## Development Practices

### Testing
Tests use pytest with pytest-mock for unit testing. Run with:
```
pytest
```

For coverage report:
```
pytest --cov=swipe_fate
```

### Type Checking
Type annotations throughout the codebase, checked with mypy:
```
mypy src
```

### Linting and Formatting
Uses ruff for code quality and formatting:
```
ruff check .
ruff format .
```