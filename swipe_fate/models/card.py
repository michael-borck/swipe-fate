from typing import Dict, Optional, Union

from pydantic import BaseModel, HttpUrl


class CardChoice(BaseModel):
    """Represents a player decision option on a card."""

    text: str
    effects: Dict[str, int]
    next_card: Optional[str] = None


class Card(BaseModel):
    """Represents a game card with a situation and choices."""

    id: str
    title: str
    text: str
    image: Union[str, HttpUrl]
    choices: Dict[str, CardChoice]

    @property
    def left_choice(self) -> CardChoice:
        """
        Returns the left choice (left swipe option).

        Returns:
            CardChoice: The left choice
        """
        return self.choices["left"]

    @property
    def right_choice(self) -> CardChoice:
        """
        Returns the right choice (right swipe option).

        Returns:
            CardChoice: The right choice
        """
        return self.choices["right"]

    def get_next_card_id(self, direction: str) -> Optional[str]:
        """
        Gets the ID of the next card based on the choice direction.

        Args:
            direction: "left" or "right" to indicate the choice made

        Returns:
            Optional[str]: The ID of the next card if specified, or None
        """
        if direction not in self.choices:
            return None

        return self.choices[direction].next_card
