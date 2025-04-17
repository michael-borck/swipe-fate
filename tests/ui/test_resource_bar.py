import pytest


# Mock flet classes and functions
@pytest.fixture
def mock_flet(mocker):
    """Mock the flet module and its components"""
    # Mock the entire flet module first
    mock_module = mocker.MagicMock()
    mocker.patch("swipe_verse.ui.components.resource_bar.ft", mock_module)

    # Set up required attributes that ResourceBar uses
    mock_module.Row = mocker.MagicMock()
    mock_module.Container = mocker.MagicMock()
    mock_module.Image = mocker.MagicMock()
    mock_module.Stack = mocker.MagicMock()
    mock_module.Tooltip = mocker.MagicMock()

    # Mock all the constants
    mock_module.MainAxisAlignment = mocker.MagicMock()
    mock_module.MainAxisAlignment.SPACE_BETWEEN = "SPACE_BETWEEN"
    mock_module.alignment = mocker.MagicMock()
    mock_module.alignment.top_center = "top_center"
    mock_module.ImageFit = mocker.MagicMock()
    mock_module.ImageFit.CONTAIN = "CONTAIN"
    mock_module.colors = mocker.MagicMock()
    mock_module.colors.GREY_400 = "GREY_400"
    mock_module.ClipBehavior = mocker.MagicMock()
    mock_module.ClipBehavior.HARD_EDGE = "HARD_EDGE"

    # Allow for UserControl (we'll monkey patch the class later)
    mock_module.UserControl = type(
        "UserControl", (), {"__init__": lambda self, **kwargs: None}
    )

    return mock_module


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
def resource_bar(mock_flet, sample_resources, sample_icons, mocker):
    """Create a ResourceBar instance for testing"""
    # Patch the module import to use our mocked version
    import sys
    from types import ModuleType

    # Create a fake ft module
    fake_ft = ModuleType("ft")
    sys.modules["ft"] = fake_ft

    # Transfer all mock attributes to the fake module
    for attr_name in dir(mock_flet):
        if not attr_name.startswith("_") or attr_name == "__init__":
            setattr(fake_ft, attr_name, getattr(mock_flet, attr_name))

    # Now import ResourceBar using the patched module
    from swipe_verse.ui.components.resource_bar import ResourceBar

    # Create and return the instance
    resource_bar = ResourceBar(resources=sample_resources, resource_icons=sample_icons)
    return resource_bar


def test_resource_bar_creation(resource_bar, sample_resources, sample_icons):
    """Test that the ResourceBar is created properly with the given resources"""
    assert resource_bar.resources == sample_resources
    assert resource_bar.resource_icons == sample_icons
    assert resource_bar.resource_controls == {}


def test_resource_bar_build(resource_bar, sample_resources, mocker, mock_flet):
    """Test the build method creates the right UI structure with mocked Row"""
    # Create a mock for the Row that will be returned
    mock_row = mocker.MagicMock()
    mock_flet.Row.return_value = mock_row

    # Create a mock icon to be returned by _create_resource_icon
    mock_icon = mocker.MagicMock()
    mocker.patch.object(resource_bar, "_create_resource_icon", return_value=mock_icon)

    # Call the build method
    result = resource_bar.build()

    # Verify Row was created with correct parameters
    mock_flet.Row.assert_called_once_with(
        alignment=mock_flet.MainAxisAlignment.SPACE_BETWEEN, spacing=10
    )

    # Verify the resource icon creation was called for each resource
    assert resource_bar._create_resource_icon.call_count == len(sample_resources)

    # Verify each icon was added to the row
    assert mock_row.controls.append.call_count == len(sample_resources)

    # Verify resource_controls were populated
    assert len(resource_bar.resource_controls) == len(sample_resources)

    # Return value should be the row
    assert result == mock_row


def test_create_resource_icon(resource_bar, sample_icons, mocker, mock_flet):
    """Test the resource icon creation method with mocked components"""
    resource_id = "resource1"
    value = 75

    # Create mocks for the UI components
    mock_filled_icon = mocker.MagicMock()
    mock_unfilled_icon = mocker.MagicMock()
    mock_container = mocker.MagicMock()
    mock_stack = mocker.MagicMock()
    mock_tooltip = mocker.MagicMock()

    # Set up returns for the mocked components
    mock_flet.Image.side_effect = [mock_filled_icon, mock_unfilled_icon]
    mock_flet.Container.return_value = mock_container
    mock_flet.Stack.return_value = mock_stack
    mock_flet.Tooltip.return_value = mock_tooltip

    # Call the method
    result = resource_bar._create_resource_icon(resource_id, value)

    # Verify Image creation
    assert mock_flet.Image.call_count == 2
    mock_flet.Image.assert_any_call(
        src=sample_icons[resource_id],
        width=50,
        height=50,
        fit=mock_flet.ImageFit.CONTAIN,
    )

    # Verify Container creation with correct height calculation
    unfilled_height = (100 - value) / 100 * 50  # 12.5px for 75% fill
    mock_flet.Container.assert_called_once()
    container_args = mock_flet.Container.call_args[1]
    assert container_args["clip_behavior"] == mock_flet.ClipBehavior.HARD_EDGE
    assert container_args["height"] == unfilled_height
    assert container_args["alignment"] == mock_flet.alignment.top_center

    # Verify Stack creation
    mock_flet.Stack.assert_called_once()
    stack_args = mock_flet.Stack.call_args[1]
    assert mock_filled_icon in stack_args["controls"]
    assert mock_container in stack_args["controls"]

    # Verify Tooltip creation
    mock_flet.Tooltip.assert_called_once_with(message="Resource1", content=mock_stack)

    # Verify the result
    assert result == mock_tooltip


def test_update_resource(resource_bar, mocker):
    """Test updating a resource value"""
    # Set up test data
    resource_id = "resource1"
    new_value = 40

    # Create mock UI components
    mock_unfilled = mocker.MagicMock()
    mock_stack = mocker.MagicMock()
    mock_stack.controls = [mocker.MagicMock(), mock_unfilled]

    mock_tooltip = mocker.MagicMock()
    mock_tooltip.content = mock_stack

    # Set up resource_controls
    resource_bar.resource_controls = {resource_id: mock_tooltip}

    # Call update_resource
    resource_bar.update_resource(resource_id, new_value)

    # Verify resource value was updated
    assert resource_bar.resources[resource_id] == new_value

    # Verify container height was updated
    expected_height = (100 - new_value) / 100 * 50  # 30px for 40% fill
    assert mock_unfilled.height == expected_height

    # Verify stack.update was called
    mock_stack.update.assert_called_once()


def test_update_all_resources(resource_bar, mocker):
    """Test updating all resources"""
    # Mock update_resource method
    mock_update = mocker.patch.object(resource_bar, "update_resource")

    # Create test data
    new_resources = {
        "resource1": 20,
        "resource2": 30,
        "resource3": 40,
        "resource4": 50,
    }

    # Call update_all_resources
    resource_bar.update_all_resources(new_resources)

    # Verify update_resource was called for each resource
    assert mock_update.call_count == len(new_resources)

    # Verify calls were made with correct parameters
    expected_calls = [
        mocker.call(resource_id, value) for resource_id, value in new_resources.items()
    ]
    mock_update.assert_has_calls(expected_calls, any_order=True)
