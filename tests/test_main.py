import sys
import pytest
from unittest.mock import patch


@pytest.fixture
def mock_args():
    """Mock command line arguments"""
    class MockArgs:
        config = None
        assets = None
        port = 0
        mode = "ui"
    
    return MockArgs()


@pytest.fixture
def mock_argparse(mocker, mock_args):
    """Mock argparse.ArgumentParser"""
    mock_parser = mocker.MagicMock()
    mock_parser.parse_args.return_value = mock_args
    
    # Mock the ArgumentParser constructor to return our mock parser
    mocker.patch("argparse.ArgumentParser", return_value=mock_parser)
    
    return mock_parser


def test_main_ui_mode(mock_argparse, mock_args, mocker):
    """Test the main function in UI mode"""
    # Import the module after mocking
    from swipe_verse.__main__ import main
    
    # Set the mode to UI
    mock_args.mode = "ui"
    
    # Mock the Flet app function
    mock_ft_app = mocker.patch("flet.app")
    
    # Mock the SwipeVerseApp import and constructor
    mock_swipe_verse_app = mocker.patch("swipe_verse.ui.app.SwipeVerseApp")
    
    # Call the main function
    result = main()
    
    # Check that the UI app was launched
    mock_ft_app.assert_called_once()
    
    # Get the target function that was passed to ft.app
    target_func = mock_ft_app.call_args[1]["target"]
    
    # Create a mock page
    mock_page = mocker.MagicMock()
    
    # Call the target function with the mock page
    target_func(mock_page)
    
    # Verify SwipeVerseApp was created with the correct arguments
    mock_swipe_verse_app.assert_called_once_with(
        page=mock_page, 
        config_path=mock_args.config, 
        assets_path=mock_args.assets
    )
    
    # Verify page.add was called with the app
    mock_page.add.assert_called_once_with(mock_swipe_verse_app.return_value)
    
    # Check that the main function returned success
    assert result == 0


def test_main_tui_mode(mock_argparse, mock_args, mocker):
    """Test the main function in TUI mode"""
    # Import the module after mocking
    from swipe_verse.__main__ import main
    
    # Set the mode to TUI
    mock_args.mode = "tui"
    
    # Mock the TUI app module
    mock_tui_module = mocker.MagicMock()
    mock_tui_module.run_tui = mocker.MagicMock()
    sys.modules["swipe_verse.tui.tui_app"] = mock_tui_module
    
    # Set config and assets paths
    mock_args.config = "test_config.json"
    mock_args.assets = "test_assets"
    
    # Call the main function
    result = main()
    
    # Check that the TUI app was launched with correct arguments
    mock_tui_module.run_tui.assert_called_once_with("test_config.json", "test_assets")
    
    # Check that the main function returned success
    assert result == 0


def test_main_cli_mode(mock_argparse, mock_args, mocker):
    """Test the main function in CLI mode"""
    # Import the module after mocking
    from swipe_verse.__main__ import main
    
    # Set the mode to CLI
    mock_args.mode = "cli"
    
    # Mock the CLI app module
    mock_cli_module = mocker.MagicMock()
    mock_cli_module.run_cli = mocker.MagicMock()
    sys.modules["swipe_verse.cli.cli_app"] = mock_cli_module
    
    # Call the main function
    result = main()
    
    # Check that the CLI app was launched
    mock_cli_module.run_cli.assert_called_once_with(None, None)
    
    # Check that the main function returned success
    assert result == 0


def test_module_execution(mocker):
    """Test execution of the module using direct function call"""
    # Since testing the if __name__ == "__main__" block directly is tricky,
    # let's just test the functionality it would execute
    
    from swipe_verse.__main__ import main
    
    # Mock the main function to prevent actual execution
    mock_main = mocker.patch("swipe_verse.__main__.main", return_value=42)
    
    # Directly call the condition that would be checked in __main__.py
    if __name__ == "__main__":  # This won't execute in the test context
        sys.exit(main())
    
    # Alternative test approach: verify main can be imported and called
    assert callable(main)
    
    # Run main() with proper mocks in place
    mock_argparse = mocker.patch("argparse.ArgumentParser")
    mock_args = mocker.MagicMock()
    mock_args.mode = "ui"
    mock_argparse.return_value.parse_args.return_value = mock_args
    
    # Mock ft.app to prevent actual app launch
    mocker.patch("flet.app")
    
    # Mock the app import
    mocker.patch("swipe_verse.ui.app.SwipeVerseApp")
    
    # Call main and check return value
    result = main()
    assert result == 0