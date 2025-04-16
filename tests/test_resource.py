
from swipe_verse.models.resource import Resource


def test_resource_initialization():
    # Test default initialization
    resource = Resource(id="gold", name="Gold", current_value=50)
    assert resource.id == "gold"
    assert resource.name == "Gold"
    assert resource.current_value == 50
    assert resource.min_value == 0
    assert resource.max_value == 100
    assert resource.icon_path is None

    # Test initialization with custom bounds
    resource = Resource(id="energy", name="Energy", current_value=5, min_value=0, max_value=10)
    assert resource.min_value == 0
    assert resource.max_value == 10
    assert resource.current_value == 5


def test_resource_adjust():
    # Create test resource
    resource = Resource(id="gold", name="Gold", current_value=50)
    
    # Test increasing within bounds
    assert resource.adjust(10) == 60
    assert resource.current_value == 60
    
    # Test decreasing within bounds
    assert resource.adjust(-20) == 40
    assert resource.current_value == 40
    
    # Test upper bounds
    resource.current_value = 90
    assert resource.adjust(20) == 100  # Should cap at max_value
    assert resource.current_value == 100
    
    # Test lower bounds
    resource.current_value = 10
    assert resource.adjust(-20) == 0  # Should cap at min_value
    assert resource.current_value == 0


def test_resource_set_value():
    # Create test resource
    resource = Resource(id="gold", name="Gold", current_value=50)
    
    # Test setting to valid value
    assert resource.set_value(75) == 75
    assert resource.current_value == 75
    
    # Test setting beyond max
    assert resource.set_value(150) == 100
    assert resource.current_value == 100
    
    # Test setting below min
    assert resource.set_value(-10) == 0
    assert resource.current_value == 0


def test_resource_get_percentage():
    # Test with default range (0-100)
    resource = Resource(id="gold", name="Gold", current_value=50)
    assert resource.get_percentage() == 50.0
    
    resource.current_value = 0
    assert resource.get_percentage() == 0.0
    
    resource.current_value = 100
    assert resource.get_percentage() == 100.0
    
    # Test with custom range (0-10)
    resource = Resource(id="energy", name="Energy", current_value=5, min_value=0, max_value=10)
    assert resource.get_percentage() == 50.0
    
    # Test with negative min range (-100 to 100)
    resource = Resource(id="temperature", name="Temperature", current_value=0, 
                        min_value=-100, max_value=100)
    assert resource.get_percentage() == 50.0
    
    resource.current_value = -100
    assert resource.get_percentage() == 0.0
    
    resource.current_value = 100
    assert resource.get_percentage() == 100.0
    
    # Test with min=max edge case
    resource = Resource(id="fixed", name="Fixed", current_value=5, min_value=5, max_value=5)
    assert resource.get_percentage() == 100.0