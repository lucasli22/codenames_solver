from pydantic import BaseModel
from enum import Enum


class Identity(Enum):
    RED_AGENT = "red_agent"
    BLUE_AGENT = "blue_agent"
    NEUTRAL = "neutral"
    ASSASSIN = "assassin"


class Card(BaseModel):
    word: str
    identity: Identity | None
    is_revealed: bool


class Hint(BaseModel):
    clue: str
    num: int
    guesses: list[str]


class GameState(Enum):
    RED_SPYMASTER = "red_spymaster"
    BLUE_SPYMASTER = "blue_spymaster"
    RED_OPERATIVE = "red_operative"
    BLUE_OPERATIVE = "blue_operative"


class Game(BaseModel):
    board: list[list[Card]]
    game_state: GameState
    red_hints: list[Hint]
    blue_hints: list[Hint]

class CreateSpymasterGameRequest(BaseModel):
    words: list[Card]

class CreateOperativeGameRequest(BaseModel):
    words: list[str]
    first_team: GameState