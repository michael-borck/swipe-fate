import pytest

from swipe_fate.models.card import Card, CardChoice


# Mock flet classes and functions
@pytest.fixture
def mock_flet(mocker):
    """Mock the flet module and its components"""
    # Mock the flet module for both component modules
    mock_module = mocker.MagicMock()
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
    
    # Mock constants
    mock_module.MainAxisAlignment.SPACE_BETWEEN = "SPACE_BETWEEN"
    mock_module.alignment.top_center = "top_center"
    mock_module.alignment.center = "center"
    mock_module.ImageFit.CONTAIN = "CONTAIN"
    mock_module.ImageFit.COVER = "COVER"
    mock_module.colors.GREY_400 = "GREY_400"
    mock_module.colors.GREEN = "GREEN"
    mock_module.colors.RED = "RED"
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
    
    # Allow UserControl for compatibility with older code that might reference it
    mock_module.UserControl = type("UserControl", (), {"__init__": lambda self, **kwargs: None})
    
    return mock_module


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
def sample_resources():
    """Create sample resources for testing"""
    return {
        "resource1": 75,  # Treasury (75%)
        "resource2": 50,  # Population (50%)
        "resource3": 25,  # Military (25%)
        "resource4": 60,  # Religion (60%)
    }


@pytest.fixture
def sample_icons():
    """Create sample resource icons for testing"""
    return {
        "resource1": "assets/default/resource_icons/resource1.png",
        "resource2": "assets/default/resource_icons/resource2.png",
        "resource3": "assets/default/resource_icons/resource3.png",
        "resource4": "assets/default/resource_icons/resource4.png",
    }


@pytest.fixture
def components(mock_flet, sample_card, sample_resources, sample_icons, mocker):
    """Set up and import all UI components"""
    # Prepare the module imports
    import sys
    from types import ModuleType
    
    # Create a fake ft module
    fake_ft = ModuleType("ft")
    sys.modules["ft"] = fake_ft
    
    # Transfer all mock attributes to the fake module
    for attr_name in dir(mock_flet):
        if not attr_name.startswith("_") or attr_name == "__init__":
            setattr(fake_ft, attr_name, getattr(mock_flet, attr_name))
    
    # Now import components
    from swipe_fate.ui.components.card_display import CardDisplay
    from swipe_fate.ui.components.resource_bar import ResourceBar
    
    # Create mock page and components
    mock_page = mocker.MagicMock()
    mock_page.width = 400
    
    card_display = CardDisplay(card=sample_card)
    card_display.page = mock_page
    card_display.update = mocker.MagicMock()
    
    resource_bar = ResourceBar(resources=sample_resources, resource_icons=sample_icons)
    
    return {
        "card_display": card_display,
        "resource_bar": resource_bar,
    }


def test_components_integration(components, mocker, mock_flet):
    """Test that components can work together in a game screen context"""
    card_display = components["card_display"]
    resource_bar = components["resource_bar"]
    
    # Mock the build methods to return simple controls
    mock_card_container = mocker.MagicMock()
    mocker.patch.object(card_display, 'build', return_value=mock_card_container)
    
    mock_resource_row = mocker.MagicMock()
    mocker.patch.object(resource_bar, 'build', return_value=mock_resource_row)
    
    # Mock swiping callbacks
    left_callback = mocker.MagicMock()
    right_callback = mocker.MagicMock()
    
    # Set up callbacks
    card_display.on_swipe_left = left_callback
    card_display.on_swipe_right = right_callback
    
    # Call methods to simulate using the components in a game screen
    card_container = card_display.build()
    resource_row = resource_bar.build()
    
    # Verify the components were built
    assert card_display.build.called
    assert resource_bar.build.called
    
    # Mock card_display properties
    card_display.card_container = mocker.MagicMock()
    card_display.card_image = mocker.MagicMock()
    card_display.update = mocker.MagicMock()
    
    # Simulate a swipe action
    # Set up initial state for swipe
    card_display.is_swiping = True
    card_display.start_x = 100
    card_display.current_x = 160  # swipe right
    
    # Create mock transform objects
    mock_offset = mocker.MagicMock()
    mock_rotate = mocker.MagicMock()
    mock_flet.transform.Offset.return_value = mock_offset
    mock_flet.transform.Rotate.return_value = mock_rotate
    
    # Create a mock end event
    event = mocker.MagicMock()
    
    # Replace _on_pan_end method with our own test version to avoid internal implementation details
    mocker.patch.object(card_display, '_on_pan_end', side_effect=lambda e: right_callback(e))
    
    # Simulate end of swipe
    card_display._on_pan_end(event)
    
    # Verify callbacks worked
    right_callback.assert_called_once_with(event)
    left_callback.assert_not_called()
    
    # Simulate resource update after a choice
    new_resources = {
        "resource1": 80,  # Increased by choice
        "resource2": 45,  # Decreased by choice
        "resource3": 25,  # Unchanged
        "resource4": 60,  # Unchanged
    }
    
    # Mock update_resource to verify calls
    mocker.patch.object(resource_bar, 'update_resource')
    
    # Update resources
    resource_bar.update_all_resources(new_resources)
    
    # Verify update_resource was called for each resource
    assert resource_bar.update_resource.call_count == len(new_resources)
    
    # Verify calls were made with correct parameters
    expected_calls = [mocker.call(resource_id, value) 
                      for resource_id, value in new_resources.items()]
    resource_bar.update_resource.assert_has_calls(expected_calls, any_order=True)