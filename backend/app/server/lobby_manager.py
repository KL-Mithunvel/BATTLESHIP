import secrets
import string
from typing import Optional

_CODE_CHARS = string.ascii_uppercase + string.digits

from .lobby import Lobby, LobbyStatus
from ..game.player import Player
from ..game.engine import GameEngine


class LobbyManager:
    def __init__(self) -> None:
        self._lobbies: dict[str, Lobby] = {}

    def create(self, host_id: str, username: str) -> Lobby:
        code = self._unique_code()
        lobby = Lobby(code=code, host_id=host_id, players={host_id: Player(host_id, username)})
        self._lobbies[code] = lobby
        return lobby

    def join(self, code: str, player_id: str, username: str) -> tuple[Optional[Lobby], str]:
        lobby = self._lobbies.get(code)
        if not lobby:
            return None, "Lobby not found"
        if lobby.status != LobbyStatus.WAITING_FOR_PLAYER:
            return None, "Lobby is not accepting players"
        if lobby.is_full():
            return None, "Lobby is full"
        lobby.players[player_id] = Player(player_id, username)
        lobby.status = LobbyStatus.PLAYERS_JOINED
        return lobby, ""

    def get(self, code: str) -> Optional[Lobby]:
        return self._lobbies.get(code)

    def start_placement(self, code: str) -> None:
        self._lobbies[code].status = LobbyStatus.SHIP_PLACEMENT

    def start_game(self, code: str) -> None:
        lobby = self._lobbies[code]
        ids = lobby.player_ids()
        lobby.engine = GameEngine(lobby.players[ids[0]], lobby.players[ids[1]])
        lobby.status = LobbyStatus.IN_PROGRESS

    def close(self, code: str) -> None:
        self._lobbies.pop(code, None)

    def _unique_code(self) -> str:
        # DR-3: cryptographic randomness, alphanumeric-only for easy sharing
        while True:
            code = ''.join(secrets.choice(_CODE_CHARS) for _ in range(6))
            if code not in self._lobbies:
                return code


lobby_manager = LobbyManager()
