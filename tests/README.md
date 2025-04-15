# SwipeFate Tests

This directory contains unit and integration tests for the SwipeFate application.

## Running Tests

To run all tests:

```bash
pytest
```

To run tests with coverage:

```bash
pytest --cov=swipe_fate
```

To run a specific test file:

```bash
pytest tests/test_resource_loader.py
```

## Test Structure

- `test_resource_loader.py`: Tests for the ResourceLoader class
- `test_ui_manager.py`: Tests for the UIManager class and integration with flet

## Notes on Testing flet Applications

Because Flet is a UI framework, some components may be challenging to test in isolation. The approach here uses mocks to test the logic without requiring a UI render context.