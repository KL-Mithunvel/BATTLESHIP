import pytest
from app.server.lobby_manager import LobbyManager
from app.server.lobby import LobbyStatus
from app.game.rules import build_ships
from tests.conftest import STANDARD_PLACEMENTS


@pytest.fixture
def manager():
    return LobbyManager()


def _place_fleet_on_lobby(lobby, player_id):
    ships = build_ships(STANDARD_PLACEMENTS)
    for p, ship in zip(STANDARD_PLACEMENTS, ships):
        lobby.players[player_id].board.place_ship(ship, p["row"], p["col"], p["horizontal"])
    lobby.players[player_id].ships_placed = True


# ── Create ────────────────────────────────────────────────────────────────────

class TestCreate:
    def test_creates_lobby(self, manager):
        lobby = manager.create("p1", "Alice")
        assert manager.get(lobby.code) is lobby

    def test_host_is_in_players(self, manager):
        lobby = manager.create("p1", "Alice")
        assert "p1" in lobby.players

    def test_initial_status_is_waiting(self, manager):
        lobby = manager.create("p1", "Alice")
        assert lobby.status == LobbyStatus.WAITING_FOR_PLAYER

    def test_codes_are_unique(self, manager):
        codes = {manager.create(f"p{i}", f"Player{i}").code for i in range(30)}
        assert len(codes) == 30

    def test_code_is_alphanumeric(self, manager):
        lobby = manager.create("p1", "Alice")
        assert lobby.code.isalnum()

    def test_code_max_length(self, manager):
        lobby = manager.create("p1", "Alice")
        assert len(lobby.code) <= 6


# ── Join ──────────────────────────────────────────────────────────────────────

class TestJoin:
    def test_join_waiting_lobby(self, manager):
        lobby = manager.create("p1", "Alice")
        result, error = manager.join(lobby.code, "p2", "Bob")
        assert result is not None
        assert error == ""

    def test_joiner_added_to_players(self, manager):
        lobby = manager.create("p1", "Alice")
        manager.join(lobby.code, "p2", "Bob")
        assert "p2" in lobby.players

    def test_status_becomes_players_joined(self, manager):
        lobby = manager.create("p1", "Alice")
        manager.join(lobby.code, "p2", "Bob")
        assert lobby.status == LobbyStatus.PLAYERS_JOINED

    def test_join_nonexistent_lobby(self, manager):
        result, error = manager.join("XXXXXX", "p2", "Bob")
        assert result is None
        assert "not found" in error.lower()

    def test_join_full_lobby_rejected(self, manager):
        lobby = manager.create("p1", "Alice")
        manager.join(lobby.code, "p2", "Bob")
        result, error = manager.join(lobby.code, "p3", "Charlie")
        assert result is None
        assert error  # status is PLAYERS_JOINED so returns "not accepting players"

    def test_join_in_progress_lobby_rejected(self, manager):
        lobby = manager.create("p1", "Alice")
        manager.join(lobby.code, "p2", "Bob")
        manager.start_placement(lobby.code)
        result, error = manager.join(lobby.code, "p3", "Charlie")
        assert result is None
        assert "not accepting" in error.lower()

    def test_code_case_insensitive_via_upper(self, manager):
        lobby = manager.create("p1", "Alice")
        result, _ = manager.join(lobby.code.upper(), "p2", "Bob")
        assert result is not None


# ── start_placement / start_game ──────────────────────────────────────────────

class TestGameLifecycle:
    def test_start_placement_updates_status(self, manager):
        lobby = manager.create("p1", "Alice")
        manager.join(lobby.code, "p2", "Bob")
        manager.start_placement(lobby.code)
        assert lobby.status == LobbyStatus.SHIP_PLACEMENT

    def test_start_game_creates_engine(self, manager):
        lobby = manager.create("p1", "Alice")
        manager.join(lobby.code, "p2", "Bob")
        _place_fleet_on_lobby(lobby, "p1")
        _place_fleet_on_lobby(lobby, "p2")
        manager.start_game(lobby.code)
        assert lobby.engine is not None

    def test_start_game_status_is_in_progress(self, manager):
        lobby = manager.create("p1", "Alice")
        manager.join(lobby.code, "p2", "Bob")
        _place_fleet_on_lobby(lobby, "p1")
        _place_fleet_on_lobby(lobby, "p2")
        manager.start_game(lobby.code)
        assert lobby.status == LobbyStatus.IN_PROGRESS

    def test_close_removes_lobby(self, manager):
        lobby = manager.create("p1", "Alice")
        code = lobby.code
        manager.close(code)
        assert manager.get(code) is None

    def test_close_nonexistent_is_safe(self, manager):
        manager.close("ZZZZZZ")  # should not raise
