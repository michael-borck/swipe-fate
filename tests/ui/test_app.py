import pytest
import flet as ft
import sys
from pathlib import Path

from swipe_fate.ui.app import SwipeFateApp


# Mock flet classes and functions
@pytest.fixture
def mock_flet(mocker):
    """Mock the flet module and its components"""
    # Mock the flet module
    mock_module = mocker.MagicMock()
    mocker.patch("swipe_fate.ui.app.ft", mock_module)
    mocker.patch("swipe_fate.ui.title_screen.ft", mock_module)
    mocker.patch("swipe_fate.ui.game_screen.ft", mock_module)
    mocker.patch("swipe_fate.ui.settings_screen.ft", mock_module)
    
    # Set up required attributes
    mock_module.Container = mocker.MagicMock()
    mock_module.Column = mocker.MagicMock()
    mock_module.Row = mocker.MagicMock()
    mock_module.Text = mocker.MagicMock()
    mock_module.ProgressRing = mocker.MagicMock()
    mock_module.SnackBar = mocker.MagicMock()
    mock_module.Page = mocker.MagicMock()
    
    # Mock constants
    mock_module.ThemeMode = mocker.MagicMock()
    mock_module.ThemeMode.SYSTEM = "SYSTEM"
    mock_module.CrossAxisAlignment = mocker.MagicMock()
    mock_module.CrossAxisAlignment.CENTER = "CENTER"
    mock_module.MainAxisAlignment = mocker.MagicMock()
    mock_module.MainAxisAlignment.CENTER = "CENTER"
    mock_module.alignment = mocker.MagicMock()
    mock_module.alignment.center = "center"
    
    return mock_module


@pytest.fixture
def mock_services(mocker):
    """Mock service classes"""
    mock_config_loader = mocker.MagicMock()
    mocker.patch("swipe_fate.ui.app.ConfigLoader", return_value=mock_config_loader)
    
    mock_asset_manager = mocker.MagicMock()
    mocker.patch("swipe_fate.ui.app.AssetManager", return_value=mock_asset_manager)
    
    mock_image_processor = mocker.MagicMock()
    mocker.patch("swipe_fate.ui.app.ImageProcessor", return_value=mock_image_processor)
    
    return {
        "config_loader": mock_config_loader,
        "asset_manager": mock_asset_manager,
        "image_processor": mock_image_processor
    }


@pytest.fixture
def mock_screens(mocker):
    """Mock screen classes"""
    # We need to patch at the importing location since these are imported inside a method
    mocker.patch.dict("sys.modules", {
        "swipe_fate.ui.title_screen": mocker.MagicMock(),
        "swipe_fate.ui.game_screen": mocker.MagicMock(),
        "swipe_fate.ui.settings_screen": mocker.MagicMock(),
    })
    
    # Create mock screens
    mock_title_screen = mocker.MagicMock()
    mock_game_screen = mocker.MagicMock()
    mock_settings_screen = mocker.MagicMock()
    
    # Set up TitleScreen mock
    title_screen_module = sys.modules["swipe_fate.ui.title_screen"]
    title_screen_module.TitleScreen = mocker.MagicMock(return_value=mock_title_screen)
    
    # Set up GameScreen mock
    game_screen_module = sys.modules["swipe_fate.ui.game_screen"]
    game_screen_module.GameScreen = mocker.MagicMock(return_value=mock_game_screen)
    
    # Set up SettingsScreen mock
    settings_screen_module = sys.modules["swipe_fate.ui.settings_screen"]
    settings_screen_module.SettingsScreen = mocker.MagicMock(return_value=mock_settings_screen)
    
    return {
        "title_screen": mock_title_screen,
        "title_screen_class": title_screen_module.TitleScreen,
        "game_screen": mock_game_screen,
        "game_screen_class": game_screen_module.GameScreen,
        "settings_screen": mock_settings_screen,
        "settings_screen_class": settings_screen_module.SettingsScreen
    }


@pytest.fixture
def mock_game_state(mocker):
    """Mock game state and logic"""
    mock_state = mocker.MagicMock()
    mock_state_class = mocker.patch("swipe_fate.ui.app.GameState")
    mock_state_class.new_game.return_value = mock_state
    
    mock_logic = mocker.MagicMock()
    mock_logic_class = mocker.patch("swipe_fate.ui.app.GameLogic")
    mock_logic_class.return_value = mock_logic
    
    return {
        "state": mock_state,
        "state_class": mock_state_class,
        "logic": mock_logic,
        "logic_class": mock_logic_class
    }


@pytest.fixture
def mock_page(mocker):
    """Create a mock Page object"""
    mock_page = mocker.MagicMock()
    mock_page.width = 800
    mock_page.controls = []
    mock_page.overlay = []
    mock_page.update = mocker.AsyncMock()
    mock_page.run_async = mocker.AsyncMock()
    
    # Mock async run_async to actually call the function
    async def mock_run_async(func):
        if callable(func):
            return await func
        else:
            return await func()
            
    mock_page.run_async.side_effect = mock_run_async
    
    return mock_page


@pytest.fixture
def app(mock_flet, mock_services, mock_game_state, mock_page, mocker):
    """Create a SwipeFateApp instance for testing"""
    # Allow the Path.__file__ to be used
    mocker.patch("swipe_fate.ui.app.Path", autospec=True)
    
    # Create the app
    app = SwipeFateApp(page=mock_page)
    
    # Connect the mocks
    app.config_loader = mock_services["config_loader"]
    app.asset_manager = mock_services["asset_manager"]
    app.image_processor = mock_services["image_processor"]
    
    return app


@pytest.mark.asyncio
async def test_app_initialization(app, mock_page, mock_services):
    """Test that the app is initialized properly"""
    # Verify page configuration
    assert app.page.title == "Swipe Fate"
    assert app.page.theme_mode == "SYSTEM"
    assert app.page.padding == 0
    assert app.page.on_resize is not None
    assert app.page.on_window_event is not None
    
    # Verify loading indicator
    assert len(app.page.overlay) == 1
    
    # Verify services are initialized
    assert app.config_loader is mock_services["config_loader"]
    assert app.asset_manager is mock_services["asset_manager"]
    assert app.image_processor is mock_services["image_processor"]


@pytest.mark.asyncio
async def test_handle_resize(app, mock_page, mocker):
    """Test the resize handler"""
    # Mock event
    mock_event = mocker.MagicMock()
    
    # Set up current screen
    mock_screen = mocker.MagicMock()
    app.current_screen = mock_screen
    
    # Set mobile width
    mock_page.width = 500
    
    # Call the handler
    app._handle_resize(mock_event)
    
    # Verify mobile flag was set
    assert app.is_mobile is True
    
    # Verify screen was updated
    mock_screen.update.assert_called_once()
    
    # Set desktop width
    mock_page.width = 1000
    
    # Call the handler again
    app._handle_resize(mock_event)
    
    # Verify mobile flag was updated
    assert app.is_mobile is False


@pytest.mark.asyncio
async def test_build(app, mock_flet, mock_page, mocker):
    """Test the build method"""
    # Mock run_async
    mocker.patch.object(app.page, 'run_async')
    
    # Call the build method
    result = app.build()
    
    # Verify navigate_to was scheduled
    app.page.run_async.assert_called_once()
    
    # Verify a container was returned
    assert isinstance(result, mocker.MagicMock)
    mock_flet.Container.assert_called_with(expand=True, content=app.current_screen)


@pytest.mark.asyncio
async def test_load_config_success(app, mock_services, mock_game_state, mocker):
    """Test successful config loading"""
    # Set up mock config loader to return a config
    mock_config = mocker.MagicMock()
    # Use AsyncMock for the load_config method
    app.config_loader.load_config = mocker.AsyncMock(return_value=mock_config)
    
    # Set up GameState.new_game mock
    mocker.patch("swipe_fate.ui.app.GameState.new_game", return_value=mock_game_state["state"])
    
    # Set up GameLogic mock
    mocker.patch("swipe_fate.ui.app.GameLogic", return_value=mock_game_state["logic"])
    
    # Set up mock to avoid issues with the _preload_assets method
    mocker.patch.object(app, '_preload_assets', mocker.AsyncMock())
    
    # Call the method
    success = await app.load_config("test_config.json")
    
    # Verify config loader was called
    app.config_loader.load_config.assert_awaited_once_with("test_config.json")
    
    # Verify success was returned
    assert success is True


@pytest.mark.asyncio
async def test_load_config_failure(app, mock_services, mock_page, mocker):
    """Test config loading failure"""
    # Setup mock to raise an exception
    mock_error = Exception("Test error")
    app.config_loader.load_config.side_effect = mock_error
    
    # Call the method
    success = await app.load_config("test_config.json")
    
    # Verify config loader was called
    app.config_loader.load_config.assert_called_once_with("test_config.json")
    
    # Verify error handling
    assert success is False
    assert mock_page.snack_bar is not None
    assert mock_page.snack_bar.open is True


@pytest.mark.asyncio
async def test_navigate_to_title(app, mock_page, mock_screens, mocker):
    """Test navigation to title screen"""
    # Call navigate_to
    await app.navigate_to("title")
    
    # Verify TitleScreen was created
    mock_screens["title_screen_class"].assert_called_once()
    
    # Verify the page was updated
    assert len(mock_page.controls) == 1
    assert mock_page.controls[0] == app.current_screen
    mock_page.update.assert_called_once()
    
    # Verify current_screen was set
    assert app.current_screen == mock_screens["title_screen"]


@pytest.mark.asyncio
async def test_navigate_to_settings(app, mock_page, mock_screens, mocker):
    """Test navigation to settings screen"""
    # Mock _get_current_settings
    mock_settings = {"player_name": "Test Player", "difficulty": "hard", "filter": "none"}
    mocker.patch.object(app, '_get_current_settings', return_value=mock_settings)
    
    # Call navigate_to
    await app.navigate_to("settings")
    
    # Verify SettingsScreen was created with correct parameters
    mock_screens["settings_screen_class"].assert_called_once()
    
    # Verify the on_save handler was passed
    kwargs = mock_screens["settings_screen_class"].call_args.kwargs
    assert "on_save" in kwargs
    assert kwargs["settings"] == mock_settings
    
    # Verify the page was updated
    assert len(mock_page.controls) == 1
    assert mock_page.controls[0] == app.current_screen
    
    # Verify current_screen was set
    assert app.current_screen == mock_screens["settings_screen"]


@pytest.mark.asyncio
async def test_navigate_to_game_with_state(app, mock_page, mock_screens, mock_game_state, mocker):
    """Test navigation to game screen with existing game state"""
    # Set up game state and logic
    app.game_state = mock_game_state["state"]
    app.game_logic = mock_game_state["logic"]
    
    # Call navigate_to
    await app.navigate_to("game")
    
    # Verify GameScreen was created with correct parameters
    mock_screens["game_screen_class"].assert_called_once_with(
        game_state=app.game_state,
        game_logic=app.game_logic,
        on_new_game=mocker.ANY,
        on_main_menu=mocker.ANY
    )
    
    # Verify the page was updated
    assert len(mock_page.controls) == 1
    assert mock_page.controls[0] == app.current_screen
    
    # Verify current_screen was set
    assert app.current_screen == mock_screens["game_screen"]


@pytest.mark.asyncio
async def test_navigate_to_game_without_state(app, mock_page, mocker):
    """Test navigation to game screen without existing game state"""
    # Ensure no game state
    app.game_state = None
    
    # Mock load_config to return success
    mocker.patch.object(app, 'load_config', return_value=True)
    
    # Mock navigate_to to avoid recursion
    original_navigate_to = app.navigate_to
    navigate_to_mock = mocker.AsyncMock()
    mocker.patch.object(app, 'navigate_to', navigate_to_mock)
    
    # Call the original navigate_to with game
    await original_navigate_to("game")
    
    # Verify load_config was called
    app.load_config.assert_called_once()
    
    # Verify snack bar was shown
    assert mock_page.snack_bar is not None
    assert mock_page.snack_bar.open is True


@pytest.mark.asyncio
async def test_handle_save_settings(app, mock_page, mocker):
    """Test saving settings"""
    # Set up game state
    app.game_state = mocker.MagicMock()
    
    # Mock navigate_to
    mocker.patch.object(app, 'navigate_to')
    
    # Settings to save
    settings = {
        "player_name": "New Player",
        "difficulty": "easy",
        "filter": "grayscale"
    }
    
    # Call _handle_save_settings
    app._handle_save_settings(settings)
    
    # Verify settings were updated
    assert app.game_state.player_name == "New Player"
    assert app.game_state.difficulty == "easy"
    
    # Verify page.run_async was called to navigate
    mock_page.run_async.assert_called_once()


@pytest.mark.asyncio
async def test_get_current_settings_with_game_state(app, mocker):
    """Test getting current settings with game state"""
    # Set up game state
    app.game_state = mocker.MagicMock()
    app.game_state.player_name = "Test Player"
    app.game_state.difficulty = "hard"
    
    # Call _get_current_settings
    settings = app._get_current_settings()
    
    # Verify settings were returned correctly
    assert settings["player_name"] == "Test Player"
    assert settings["difficulty"] == "hard"
    assert settings["filter"] == "none"


@pytest.mark.asyncio
async def test_get_current_settings_without_game_state(app):
    """Test getting current settings without game state"""
    # Ensure no game state
    app.game_state = None
    
    # Call _get_current_settings
    settings = app._get_current_settings()
    
    # Verify default settings were returned
    assert settings["player_name"] == "Player"
    assert settings["difficulty"] == "standard"
    assert settings["filter"] == "none"


@pytest.mark.asyncio
async def test_new_game(app, mock_game_state, mocker):
    """Test starting a new game"""
    # Set up game state and logic
    app.game_state = mock_game_state["state"]
    app.game_logic = mock_game_state["logic"]
    app.game_logic.config = mocker.MagicMock()
    app.game_state.player_name = "Test Player"
    app.game_state.difficulty = "hard"
    
    # Mock navigate_to
    mocker.patch.object(app, 'navigate_to')
    
    # Call new_game
    await app.new_game()
    
    # Verify new game state was created
    mock_game_state["state_class"].new_game.assert_called_with(
        app.game_logic.config,
        player_name="Test Player",
        difficulty="hard"
    )
    
    # Verify new game logic was created
    mock_game_state["logic_class"].assert_called_with(app.game_state, app.game_logic.config)
    
    # Verify navigate_to was called
    app.navigate_to.assert_called_once_with("game")