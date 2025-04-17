from typing import Optional

from pydantic import BaseModel


class Resource(BaseModel):
    """Represents a game resource that players need to manage during gameplay."""

    id: str
    name: str
    current_value: int
    min_value: int = 0
    max_value: int = 100
    icon_path: Optional[str] = None

    def adjust(self, amount: int) -> int:
        """
        Adjusts the resource value by the specified amount,
        keeping it within min and max bounds.

        Returns:
            int: The new resource value after adjustment
        """
        self.current_value = max(
            self.min_value, min(self.max_value, self.current_value + amount)
        )
        return self.current_value

    def set_value(self, value: int) -> int:
        """
        Sets the resource to a specific value, keeping it within min and max bounds.

        Returns:
            int: The new resource value after setting
        """
        self.current_value = max(self.min_value, min(self.max_value, value))
        return self.current_value

    def get_percentage(self) -> float:
        """
        Returns the current value as a percentage of the maximum possible value.

        Returns:
            float: Percentage between 0 and 100
        """
        range_size = self.max_value - self.min_value
        if range_size == 0:
            return 100.0  # Avoid division by zero

        relative_value = self.current_value - self.min_value
        return (relative_value / range_size) * 100.0
