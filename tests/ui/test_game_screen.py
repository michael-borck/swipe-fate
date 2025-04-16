import pytest

from swipe_verse.models.card import Card, CardChoice
from swipe_verse.models.game_state import GameState
from swipe_verse.models.resource import Resource
from swipe_verse.services.game_logic import GameLogic


# Mock flet classes and functions
@pytest.fixture
def mock_flet(mocker):
    """Mock the flet module and its components"""
    # Mock the flet module for all component modules
    mock_module = mocker.MagicMock()
    mocker.patch("swipe_fate.ui.game_screen.ft", mock_module)
    mocker.patch("swipe_fate.ui.components.card_display.ft", mock_module)
    mocker.patch("swipe_fate.ui.components.resource_bar.ft", mock_module)
    
    # Set up required attributes
    mock_module.Container = mocker.MagicMock()
    mock_module.Row = mocker.MagicMock()
    mock_module.Column = mocker.MagicMock()
    mock_module.Text = mocker.MagicMock()
    mock_module.Image = mocker.MagicMock()
    mock_module.Stack = mocker.MagicMock()
    mock_module.Tooltip = mocker.MagicMock()
    mock_module.GestureDetector = mocker.MagicMock()
    mock_module.ElevatedButton = mocker.MagicMock()
    mock_module.OutlinedButton = mocker.MagicMock()
    mock_module.AlertDialog = mocker.MagicMock()
    
    # Mock constants
    mock_module.MainAxisAlignment.SPACE_BETWEEN = "SPACE_BETWEEN"
    mock_module.MainAxisAlignment.END = "END"
    mock_module.alignment.top_center = "top_center"
    mock_module.alignment.center = "center"
    mock_module.ImageFit.CONTAIN = "CONTAIN"
    mock_module.ImageFit.COVER = "COVER"
    mock_module.colors.GREY_400 = "GREY_400"
    mock_module.colors.GREEN = "GREEN"
    mock_module.colors.RED = "RED"
    mock_module.colors.BLACK12 = "BLACK12"
    mock_module.colors.BLACK26 = "BLACK26"
    mock_module.ClipBehavior.HARD_EDGE = "HARD_EDGE"
    mock_module.TextAlign.CENTER = "CENTER"
    mock_module.MainAxisAlignment = mocker.MagicMock()
    mock_module.MainAxisAlignment.START = "START"
    mock_module.MainAxisAlignment.SPACE_AROUND = "SPACE_AROUND"
    mock_module.CrossAxisAlignment = mocker.MagicMock()
    mock_module.border = mocker.MagicMock()
    mock_module.border_radius = mocker.MagicMock()
    mock_module.AnimationCurve = mocker.MagicMock()
    mock_module.AnimationCurve.EASE_IN_OUT = "EASE_IN_OUT"
    mock_module.animation = mocker.MagicMock()
    mock_module.animation.Animation = mocker.MagicMock()
    mock_module.transform = mocker.MagicMock()
    mock_module.transform.Offset = mocker.MagicMock()
    mock_module.transform.Rotate = mocker.MagicMock()
    mock_module.border_radius.all = mocker.MagicMock()
    mock_module.margin = mocker.MagicMock()
    mock_module.margin.only = mocker.MagicMock()
    mock_module.padding = mocker.MagicMock()
    mock_module.padding.all = mocker.MagicMock()
    mock_module.FontWeight = mocker.MagicMock()
    mock_module.FontWeight.BOLD = "BOLD"
    mock_module.ButtonStyle = mocker.MagicMock()
    mock_module.RoundedRectangleBorder = mocker.MagicMock()
    
    # Allow UserControl for compatibility
    mock_module.UserControl = type("UserControl", (), {"__init__": lambda self, **kwargs: None})
    
    return mock_module


@pytest.fixture
def sample_resources():
    """Create sample resources for testing"""
    return {
        "resource1": Resource(id="resource1", name="Treasury", current_value=75, icon_path="resource1.png"),
        "resource2": Resource(id="resource2", name="Population", current_value=50, icon_path="resource2.png"),
        "resource3": Resource(id="resource3", name="Military", current_value=25, icon_path="resource3.png"),
        "resource4": Resource(id="resource4", name="Religion", current_value=60, icon_path="resource4.png"),
    }


@pytest.fixture
def sample_card():
    """Create a sample card for testing"""
    return Card(
        id="test_card_001",
        title="Test Card",
        text="This is a test card with choices.",
        image="assets/default/card_fronts/card1.png",
        choices={
            "left": CardChoice(
                text="Left Option",
                effects={"resource1": -10, "resource2": 5},
                next_card="card_002"
            ),
            "right": CardChoice(
                text="Right Option",
                effects={"resource1": 5, "resource2": -10},
                next_card="card_003"
            )
        }
    )


@pytest.fixture
def sample_game_state(sample_card, sample_resources, mocker):
    """Create a sample game state for testing"""
    # Mock theme
    mock_theme = mocker.MagicMock()
    mock_theme.resource_icons = {
        "resource1": "assets/default/resource_icons/resource1.png",
        "resource2": "assets/default/resource_icons/resource2.png",
        "resource3": "assets/default/resource_icons/resource3.png",
        "resource4": "assets/default/resource_icons/resource4.png",
    }
    
    # Mock settings
    mock_settings = mocker.MagicMock()
    mock_settings.turn_unit = "Days"
    
    # Get resource values for GameState initialization (needs to be a Dict[str, int])
    resource_values = {key: resource.current_value for key, resource in sample_resources.items()}
    
    # Create GameState with required params
    game_state = GameState(
        resources=resource_values,
        current_card=sample_card,
        settings=mock_settings,
        theme=mock_theme,
        player_name="Test Player",
    )
    
    # Override resources with our Resource objects for the tests
    game_state.resources = sample_resources
    game_state.turn_count = 10
    
    return game_state


@pytest.fixture
def sample_game_logic(sample_game_state, mocker):
    """Create a sample game logic for testing"""
    game_logic = mocker.MagicMock(spec=GameLogic)
    game_logic.calculate_popularity.return_value = 65
    game_logic.calculate_progress.return_value = 40
    return game_logic


@pytest.fixture
def mock_components(mocker):
    """Mock the UI component classes"""
    # Mock ResourceBar
    mock_resource_bar = mocker.MagicMock()
    mock_resource_bar.build.return_value = mocker.MagicMock()
    mock_resource_bar.update_all_resources = mocker.MagicMock()
    
    # Mock CardDisplay
    mock_card_display = mocker.MagicMock()
    mock_card_display.update_card = mocker.MagicMock()
    
    # Create patch for the components
    mocker.patch("swipe_fate.ui.components.resource_bar.ResourceBar", return_value=mock_resource_bar)
    mocker.patch("swipe_fate.ui.components.card_display.CardDisplay", return_value=mock_card_display)
    
    return {
        "resource_bar": mock_resource_bar,
        "card_display": mock_card_display
    }


@pytest.fixture
def game_screen(mock_flet, sample_game_state, sample_game_logic, mock_components, mocker):
    """Create a GameScreen instance for testing"""
    # Import here to use the mocked modules
    import sys
    from types import ModuleType
    
    # Create a fake ft module
    fake_ft = ModuleType("ft")
    sys.modules["ft"] = fake_ft
    
    # Transfer all mock attributes to the fake module
    for attr_name in dir(mock_flet):
        if not attr_name.startswith("_") or attr_name == "__init__":
            setattr(fake_ft, attr_name, getattr(mock_flet, attr_name))
    
    # Now import GameScreen
    from swipe_verse.ui.game_screen import GameScreen
    
    # Create mock callbacks
    on_new_game = mocker.MagicMock()
    on_main_menu = mocker.MagicMock()
    
    # Create mock page
    mock_page = mocker.MagicMock()
    mock_page.width = 400
    
    # Create GameScreen instance
    game_screen = GameScreen(
        game_state=sample_game_state,
        game_logic=sample_game_logic,
        on_new_game=on_new_game,
        on_main_menu=on_main_menu
    )
    game_screen.page = mock_page
    
    return game_screen


def test_game_screen_initialization(game_screen, sample_game_state, sample_game_logic):
    """Test that the GameScreen is initialized properly"""
    assert game_screen.game_state == sample_game_state
    assert game_screen.game_logic == sample_game_logic
    assert game_screen.card_display is None
    assert game_screen.resource_bar is None


def test_game_screen_build(game_screen, mock_flet, mocker):
    """Test the build method creates the correct UI structure"""
    # Create mock for Column that will be returned
    mock_column = mocker.MagicMock()
    mock_column.controls = []  # Create an actual list for controls
    mock_flet.Column.return_value = mock_column
    
    # Mock ResourceBar and CardDisplay CLASSES
    mock_resource_bar_class = mocker.patch("swipe_fate.ui.game_screen.ResourceBar")
    mock_resource_bar_instance = mocker.MagicMock()
    mock_resource_bar_class.return_value = mock_resource_bar_instance
    mock_resource_bar_instance.build.return_value = mocker.MagicMock()
    
    mock_card_display_class = mocker.patch("swipe_fate.ui.game_screen.CardDisplay")
    mock_card_display_instance = mocker.MagicMock()
    mock_card_display_class.return_value = mock_card_display_instance
    
    # Create mock for _create_game_stats
    mock_stats = mocker.MagicMock()
    mocker.patch.object(game_screen, '_create_game_stats', return_value=mock_stats)
    
    # Mock the ft.Text, ft.Container, etc.
    mock_text = mocker.MagicMock()
    mock_flet.Text.return_value = mock_text
    
    mock_container = mocker.MagicMock()
    mock_flet.Container.return_value = mock_container
    
    mock_row = mocker.MagicMock()
    mock_flet.Row.return_value = mock_row
    
    # Call the build method
    result = game_screen.build()
    
    # Verify Column was created
    mock_flet.Column.assert_called_once()
    
    # Verify ResourceBar and CardDisplay classes were called with correct args
    mock_resource_bar_class.assert_called_once()
    mock_card_display_class.assert_called_once()
    
    # Verify these were set on the game_screen
    assert game_screen.resource_bar is mock_resource_bar_instance
    assert game_screen.card_display is mock_card_display_instance
    
    # Verify _create_game_stats was called
    game_screen._create_game_stats.assert_called_once()
    
    # Return value should be the column
    assert result == mock_column


def test_create_game_stats(game_screen, mock_flet, sample_game_logic, mocker):
    """Test the _create_game_stats method"""
    # Create mock for Container that will be returned
    mock_container = mocker.MagicMock()
    mock_flet.Container.return_value = mock_container
    
    # Call the method
    result = game_screen._create_game_stats()
    
    # Verify that calculate_popularity and calculate_progress were called
    sample_game_logic.calculate_popularity.assert_called_once()
    sample_game_logic.calculate_progress.assert_called_once()
    
    # Verify Container was created with correct parameters
    mock_flet.Container.assert_called_once()
    
    # Return value should be the container
    assert result == mock_container


def test_handle_swipe_left(game_screen, mocker):
    """Test the _handle_swipe_left method"""
    # Create mock for _process_choice
    mocker.patch.object(game_screen, '_process_choice')
    
    # Create mock event
    event = mocker.MagicMock()
    
    # Call the method
    game_screen._handle_swipe_left(event)
    
    # Verify _process_choice was called with 'left'
    game_screen._process_choice.assert_called_once_with('left')


def test_handle_swipe_right(game_screen, mocker):
    """Test the _handle_swipe_right method"""
    # Create mock for _process_choice
    mocker.patch.object(game_screen, '_process_choice')
    
    # Create mock event
    event = mocker.MagicMock()
    
    # Call the method
    game_screen._handle_swipe_right(event)
    
    # Verify _process_choice was called with 'right'
    game_screen._process_choice.assert_called_once_with('right')


def test_process_choice(game_screen, sample_game_logic, mocker):
    """Test the _process_choice method"""
    # Set up mocks
    mocker.patch.object(game_screen, '_show_game_over_dialog')
    
    # Create mock result
    mock_result = mocker.MagicMock()
    mock_result.game_over = False
    mock_result.message = ""
    sample_game_logic.process_choice.return_value = mock_result
    
    # Set up components
    game_screen.resource_bar = mocker.MagicMock()
    game_screen.card_display = mocker.MagicMock()
    game_screen.controls = [mocker.MagicMock()]
    game_screen.controls[0].controls = [
        mocker.MagicMock(),  # resource_bar.build()
        mocker.MagicMock(),  # card_text
        mocker.MagicMock(),  # card_display
        mocker.MagicMock(),  # card_title
        mocker.MagicMock(),  # game_stats
        mocker.MagicMock(),  # decision_buttons
    ]
    game_screen.controls[0].controls[5].controls = [
        mocker.MagicMock(),  # left button
        mocker.MagicMock(),  # right button
    ]
    
    # Create mocks for _create_game_stats
    mock_stats = mocker.MagicMock()
    mocker.patch.object(game_screen, '_create_game_stats', return_value=mock_stats)
    
    # Call the method
    game_screen._process_choice('left')
    
    # Verify game_logic.process_choice was called
    sample_game_logic.process_choice.assert_called_once_with('left')
    
    # Verify resource_bar was updated
    game_screen.resource_bar.update_all_resources.assert_called_once()
    
    # Verify card_display was updated
    game_screen.card_display.update_card.assert_called_once()
    
    # Verify game stats were updated
    assert game_screen.controls[0].controls[4] == mock_stats
    
    # Verify _show_game_over_dialog was NOT called (since game_over=False)
    game_screen._show_game_over_dialog.assert_not_called()


def test_process_choice_game_over(game_screen, sample_game_logic, mocker):
    """Test the _process_choice method when game is over"""
    # Set up mocks
    mocker.patch.object(game_screen, '_show_game_over_dialog')
    
    # Create mock result with game over
    mock_result = mocker.MagicMock()
    mock_result.game_over = True
    mock_result.message = "Game Over Message"
    sample_game_logic.process_choice.return_value = mock_result
    
    # Set up components
    game_screen.resource_bar = mocker.MagicMock()
    game_screen.card_display = mocker.MagicMock()
    game_screen.controls = [mocker.MagicMock()]
    game_screen.controls[0].controls = [
        mocker.MagicMock(),  # resource_bar.build()
        mocker.MagicMock(),  # card_text
        mocker.MagicMock(),  # card_display
        mocker.MagicMock(),  # card_title
        mocker.MagicMock(),  # game_stats
        mocker.MagicMock(),  # decision_buttons
    ]
    game_screen.controls[0].controls[5].controls = [
        mocker.MagicMock(),  # left button
        mocker.MagicMock(),  # right button
    ]
    
    # Create mocks for _create_game_stats
    mock_stats = mocker.MagicMock()
    mocker.patch.object(game_screen, '_create_game_stats', return_value=mock_stats)
    
    # Call the method
    game_screen._process_choice('left')
    
    # Verify game_logic.process_choice was called
    sample_game_logic.process_choice.assert_called_once_with('left')
    
    # Verify _show_game_over_dialog was called with the result message
    game_screen._show_game_over_dialog.assert_called_once_with("Game Over Message")


def test_show_game_over_dialog(game_screen, mock_flet, mocker):
    """Test the _show_game_over_dialog method"""
    # Mock AlertDialog
    mock_dialog = mocker.MagicMock()
    mock_flet.AlertDialog.return_value = mock_dialog
    
    # Call the method
    game_screen._show_game_over_dialog("Game Over Message")
    
    # Verify AlertDialog was created
    mock_flet.AlertDialog.assert_called_once()
    
    # Verify dialog was assigned to page.dialog
    assert game_screen.page.dialog == mock_dialog
    
    # Verify dialog was opened
    assert game_screen.page.dialog.open is True
    
    # Verify page was updated
    game_screen.page.update.assert_called_once()


def test_dialog_callbacks(game_screen, mock_flet, mocker):
    """Test the dialog callback functions"""
    # Mock AlertDialog
    mock_dialog = mocker.MagicMock()
    mock_flet.AlertDialog.return_value = mock_dialog
    
    # Create mock callbacks
    on_new_game_callback = mocker.MagicMock()
    on_main_menu_callback = mocker.MagicMock()
    game_screen.on_new_game = on_new_game_callback
    game_screen.on_main_menu = on_main_menu_callback
    
    # Call the method to create dialog
    game_screen._show_game_over_dialog("Game Over Message")
    
    # Get the buttons' click handlers from the AlertDialog constructor call
    new_game_btn_handler = mock_flet.ElevatedButton.call_args_list[0][1]['on_click']
    main_menu_btn_handler = mock_flet.OutlinedButton.call_args_list[0][1]['on_click']
    
    # Create mock event
    event = mocker.MagicMock()
    
    # Call the "New Game" button handler
    new_game_btn_handler(event)
    
    # Verify dialog was closed and page updated
    assert game_screen.page.dialog.open is False
    assert game_screen.page.update.call_count == 2  # First call in _show_game_over_dialog
    
    # Verify on_new_game callback was called
    on_new_game_callback.assert_called_once()
    
    # Reset mocks
    game_screen.page.update.reset_mock()
    
    # Call the "Main Menu" button handler
    main_menu_btn_handler(event)
    
    # Verify dialog was closed and page updated
    assert game_screen.page.dialog.open is False
    assert game_screen.page.update.call_count == 1
    
    # Verify on_main_menu callback was called
    on_main_menu_callback.assert_called_once()


def test_update_method(game_screen, mocker):
    """Test the update method"""
    # Set up page mock
    game_screen.page = mocker.MagicMock()
    
    # Call the update method
    game_screen.update()
    
    # Verify page.update was called
    game_screen.page.update.assert_called_once()