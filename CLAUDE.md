# Claude Instructions for Swipe-Verse

## Environment Setup

- This project uses `uv` instead of `pip` for package management
- When installing packages, always use `uv pip install` instead of `pip install`
- The project uses a virtual environment in `.venv`

## Testing

- Run tests with: `python -m pytest`
- Run tests with coverage: `python -m pytest --cov=swipe_verse`
- Linting with: `python -m ruff check .`
- Type checking with: `python -m mypy .`

## Dependency Management

- Main dependencies are managed in `pyproject.toml`
- To install all dependencies: `uv pip install -e .`
- To install development dependencies: `uv pip install -e ".[dev]"`

## Project Organization

- Models are in `swipe_verse/models/`
- Services are in `swipe_verse/services/`
- UI components are in `swipe_verse/ui/`
- Tests are in `tests/`

## Best Practices

- All tests must pass before committing
- Maintain test coverage above 70% for non-UI components
- Follow PEP 8 style guidelines (enforced by ruff)
- Use type hints for all functions and methods