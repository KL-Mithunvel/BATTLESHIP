from dataclasses import dataclass, field
from .board import Board


@dataclass
class Player:
    player_id: str
    username: str
    board: Board = field(default_factory=Board)
    ships_placed: bool = False
    ready: bool = False
