from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, TYPE_CHECKING

from ..game.player import Player

if TYPE_CHECKING:
    from ..game.engine import GameEngine


class LobbyStatus(str, Enum):
    WAITING_FOR_PLAYER = "waiting_for_player"
    PLAYERS_JOINED = "players_joined"
    SHIP_PLACEMENT = "ship_placement"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"


@dataclass
class Lobby:
    code: str
    host_id: str
    status: LobbyStatus = LobbyStatus.WAITING_FOR_PLAYER
    players: dict[str, Player] = field(default_factory=dict)
    engine: Optional["GameEngine"] = None

    def is_full(self) -> bool:
        return len(self.players) >= 2

    def player_ids(self) -> list[str]:
        return list(self.players.keys())
