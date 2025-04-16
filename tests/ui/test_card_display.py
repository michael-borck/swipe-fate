import pytest

from swipe_fate.models.card import Card, CardChoice


# Mock flet classes and functions
@pytest.fixture
def mock_flet(mocker):
    """Mock the flet module and its components"""
    mock_flet = mocker.patch("swipe_fate.ui.components.card_display.ft")
    
    # Create mock classes for flet components
    mock_flet.Container = mocker.MagicMock()
    mock_flet.Image = mocker.MagicMock()
    mock_flet.GestureDetector = mocker.MagicMock()
    mock_flet.transform.Offset = mocker.MagicMock()
    mock_flet.transform.Rotate = mocker.MagicMock()
    mock_flet.border.all = mocker.MagicMock()
    mock_flet.border_radius.all = mocker.MagicMock()
    mock_flet.BoxShadow = mocker.MagicMock()
    mock_flet.Offset = mocker.MagicMock()
    mock_flet.alignment.center = "center"
    mock_flet.animation.Animation = mocker.MagicMock()
    mock_flet.AnimationCurve.EASE_IN_OUT = "EASE_IN_OUT"
    mock_flet.ImageFit.COVER = "COVER"
    mock_flet.colors.GREEN = "GREEN"
    mock_flet.colors.RED = "RED"
    mock_flet.colors.BLACK26 = "BLACK26"
    
    return mock_flet


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
def mock_page(mocker):
    """Create a mock Page object"""
    mock = mocker.MagicMock()
    mock.width = 400
    return mock


@pytest.fixture
def card_display(mock_flet, sample_card, mock_page, mocker):
    """Create a CardDisplay instance for testing"""
    # Import here to use the mocked flet
    from swipe_fate.ui.components.card_display import CardDisplay
    
    # Create instance
    card_display = CardDisplay(card=sample_card)
    card_display.page = mock_page
    
    # Set up mocks for component properties
    card_display.card_container = mocker.MagicMock()
    card_display.card_image = mocker.MagicMock()
    card_display.update = mocker.MagicMock()
    
    return card_display


def test_card_display_creation(card_display, sample_card):
    """Test that the CardDisplay is created properly with the given card"""
    assert card_display.card == sample_card
    assert card_display.is_swiping is False
    assert card_display.swipe_threshold == 50


def test_swipe_start(card_display, mocker):
    """Test the swipe start handler"""
    # Create a mock drag event
    event = mocker.MagicMock()
    event.local_x = 100
    
    # Call the handler
    card_display._on_pan_start(event)
    
    # Check the values were updated
    assert card_display.is_swiping is True
    assert card_display.start_x == 100
    assert card_display.current_x == 100


def test_swipe_update(card_display, mocker, mock_flet):
    """Test the swipe update handler"""
    # Set up the initial state
    card_display.is_swiping = True
    card_display.start_x = 100
    
    # Create a mock transform.Offset
    mock_offset = mocker.MagicMock()
    mock_flet.transform.Offset.return_value = mock_offset
    
    # Create a mock transform.Rotate
    mock_rotate = mocker.MagicMock()
    mock_flet.transform.Rotate.return_value = mock_rotate
    
    # Create a mock border
    mock_border = mocker.MagicMock()
    mock_flet.border.all.return_value = mock_border
    
    # Create a mock update event - moved right (positive choice)
    event = mocker.MagicMock()
    event.local_x = 150
    
    # Call the handler
    card_display._on_pan_update(event)
    
    # Check the card was transformed correctly
    assert card_display.current_x == 150
    
    # Verify transform.Offset was called with the right value
    mock_flet.transform.Offset.assert_called_with(0.5, 0)  # (150-100)/100 = 0.5
    assert card_display.card_container.offset is mock_offset
    
    # Verify transform.Rotate was called with the right value
    mock_flet.transform.Rotate.assert_called_with(0.1)  # 0.5 * 0.2 = 0.1
    assert card_display.card_container.rotate is mock_rotate
    
    # Verify border.all was called for right swipe (positive choice)
    mock_flet.border.all.assert_called_with(2, mock_flet.colors.GREEN)
    assert card_display.card_container.border is mock_border
    
    # Verify update was called
    card_display.update.assert_called_once()


def test_swipe_end_with_callback(card_display, mocker, mock_flet):
    """Test the swipe end handler with a callback"""
    # Set up callbacks
    left_callback = mocker.MagicMock()
    right_callback = mocker.MagicMock()
    card_display.on_swipe_left = left_callback
    card_display.on_swipe_right = right_callback
    
    # Create mock objects for transforms
    mock_offset = mocker.MagicMock()
    mock_flet.transform.Offset.return_value = mock_offset
    
    mock_rotate = mocker.MagicMock()
    mock_flet.transform.Rotate.return_value = mock_rotate
    
    # Set up initial state - right swipe past threshold
    card_display.is_swiping = True
    card_display.start_x = 100
    card_display.current_x = 160  # 60px right swipe, greater than threshold
    
    # Create a mock end event
    event = mocker.MagicMock()
    
    # Call the handler
    card_display._on_pan_end(event)
    
    # Check that the right swipe callback was called
    right_callback.assert_called_once_with(event)
    left_callback.assert_not_called()
    
    # Check the card was reset
    assert card_display.is_swiping is False
    mock_flet.transform.Offset.assert_called_with(0, 0)
    mock_flet.transform.Rotate.assert_called_with(0)
    
    # Verify that card container properties were updated
    assert card_display.card_container.offset is mock_offset
    assert card_display.card_container.rotate is mock_rotate
    assert card_display.card_container.border is None
    
    # Verify update was called
    card_display.update.assert_called_once()


def test_update_card(card_display):
    """Test the update_card method"""
    # Create a new card
    new_card = Card(
        id="new_test_card",
        title="New Test Card",
        text="This is a new test card.",
        image="assets/default/card_fronts/card2.png",
        choices={
            "left": CardChoice(
                text="New Left Option",
                effects={"resource1": -5, "resource2": 10},
            ),
            "right": CardChoice(
                text="New Right Option",
                effects={"resource1": 10, "resource2": -5},
            )
        }
    )
    
    # Update the card
    card_display.update_card(new_card)
    
    # Check the card was updated
    assert card_display.card == new_card
    assert card_display.card_image.src == "assets/default/card_fronts/card2.png"
    
    # Verify update was called
    card_display.update.assert_called_once()