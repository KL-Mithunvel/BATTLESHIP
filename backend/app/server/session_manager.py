import secrets
from typing import Optional


class SessionManager:
    def __init__(self) -> None:
        self._sessions: dict[str, str] = {}  # player_id → username

    def create(self, username: str) -> str:
        player_id = secrets.token_urlsafe(16)  # DR-3: cryptographic randomness
        self._sessions[player_id] = username
        return player_id

    def get_username(self, player_id: str) -> Optional[str]:
        return self._sessions.get(player_id)

    def remove(self, player_id: str) -> None:
        self._sessions.pop(player_id, None)


session_manager = SessionManager()