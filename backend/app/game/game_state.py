from dataclasses import dataclass
from enum import Enum
from typing import Optional


class GameStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


@dataclass
class GameState:
    status: GameStatus = GameStatus.IN_PROGRESS
    current_turn: Optional[str] = None
    winner: Optional[str] = None