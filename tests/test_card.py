
from swipe_verse.models.card import Card, CardChoice


def test_card_initialization():
    # Create test card choices
    left_choice = CardChoice(
        text="Go left", 
        effects={"gold": -5, "popularity": 10}, 
        next_card="card_002"
    )
    right_choice = CardChoice(text="Go right", effects={"gold": 10, "popularity": -5})
    
    # Create test card
    card = Card(
        id="card_001",
        title="Test Decision",
        text="This is a test card with a decision to make.",
        image="test_card.png",
        choices={"left": left_choice, "right": right_choice}
    )
    
    # Test basic properties
    assert card.id == "card_001"
    assert card.title == "Test Decision"
    assert card.text == "This is a test card with a decision to make."
    assert card.image == "test_card.png"
    
    # Test choices
    assert card.choices["left"].text == "Go left"
    assert card.choices["right"].text == "Go right"
    assert card.choices["left"].effects["gold"] == -5
    assert card.choices["right"].effects["gold"] == 10
    
    # Test next_card is optional
    assert card.choices["left"].next_card == "card_002"
    assert card.choices["right"].next_card is None


def test_card_properties():
    # Create test card choices
    left_choice = CardChoice(text="Go left", effects={"gold": -5}, next_card="card_002")
    right_choice = CardChoice(text="Go right", effects={"gold": 10})
    
    # Create test card
    card = Card(
        id="card_001",
        title="Test Card",
        text="Test text",
        image="test.png",
        choices={"left": left_choice, "right": right_choice}
    )
    
    # Test properties
    assert card.left_choice == left_choice
    assert card.right_choice == right_choice


def test_get_next_card_id():
    # Create test card choices
    left_choice = CardChoice(text="Go left", effects={"gold": -5}, next_card="card_002")
    right_choice = CardChoice(text="Go right", effects={"gold": 10})
    
    # Create test card
    card = Card(
        id="card_001",
        title="Test Card",
        text="Test text",
        image="test.png",
        choices={"left": left_choice, "right": right_choice}
    )
    
    # Test get_next_card_id
    assert card.get_next_card_id("left") == "card_002"
    assert card.get_next_card_id("right") is None
    assert card.get_next_card_id("invalid") is None