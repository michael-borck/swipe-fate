from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, HttpUrl


class ResourceEffect(BaseModel):
    resource_id: str
    value: int


class CardChoice(BaseModel):
    text: str
    effects: Dict[str, int]
    next_card: Optional[str] = None


class Card(BaseModel):
    id: str
    title: str
    text: str
    image: Union[str, HttpUrl]
    choices: Dict[str, CardChoice]


class WinCondition(BaseModel):
    resource: str
    min: int
    max: int


class GameStats(BaseModel):
    popularity_formula: str = Field(
        default="resource1*0.4 + resource2*0.3 + resource3*0.2 + resource4*0.1"
    )


class GameSettings(BaseModel):
    initial_resources: Dict[str, int]
    win_conditions: List[WinCondition]
    difficulty_modifiers: Dict[str, float]
    turn_unit: str = "years"
    stats: GameStats = Field(default_factory=GameStats)


class ColorScheme(BaseModel):
    primary: str
    secondary: str
    accent: str


class Theme(BaseModel):
    name: str
    card_back: Union[str, HttpUrl]
    background: Optional[Union[str, HttpUrl]] = None
    color_scheme: ColorScheme
    resource_icons: Dict[str, Union[str, HttpUrl]]
    filters: Dict[str, List[str]]


class GameInfo(BaseModel):
    title: str
    description: str
    version: str
    author: str
    backstory: Optional[str] = None
    # Licensing information for the scenario
    license: Optional[str] = Field(
        default=None,
        description="License name for the scenario, e.g., CC BY 4.0"
    )
    license_url: Optional[HttpUrl] = Field(
        default=None,
        description="URL to the full license text"
    )


class GameConfig(BaseModel):
    game_info: GameInfo
    theme: Theme
    game_settings: GameSettings
    cards: List[Card]
