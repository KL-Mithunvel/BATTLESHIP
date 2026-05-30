import pytest
from app.game.game_state import GameStatus
from tests.conftest import make_engine, sink_all_p2


# ── Turn enforcement (DR-1) ───────────────────────────────────────────────────

class TestTurnEnforcement:
    def test_p1_goes_first(self, engine):
        result = engine.fire("p1", 9, 9)  # row 9 — miss
        assert result["valid"] is True

    def test_p2_cannot_fire_first(self, engine):
        result = engine.fire("p2", 9, 9)
        assert result["valid"] is False
        assert "turn" in result["reason"].lower()

    def test_turn_switches_to_p2_after_p1_fires(self, engine):
        engine.fire("p1", 9, 9)
        assert engine.state.current_turn == "p2"

    def test_turn_switches_back_to_p1_after_p2_fires(self, engine):
        engine.fire("p1", 9, 9)
        engine.fire("p2", 9, 9)
        assert engine.state.current_turn == "p1"

    def test_p1_cannot_fire_twice_in_a_row(self, engine):
        engine.fire("p1", 9, 9)
        result = engine.fire("p1", 9, 8)
        assert result["valid"] is False


# ── Coordinate validation (DR-1) ─────────────────────────────────────────────

class TestCoordinateValidation:
    def test_valid_corner_coordinates(self, engine):
        assert engine.fire("p1", 0, 0)["valid"] is True

    def test_row_10_rejected(self, engine):
        assert engine.fire("p1", 10, 0)["valid"] is False

    def test_col_10_rejected(self, engine):
        assert engine.fire("p1", 0, 10)["valid"] is False

    def test_negative_row_rejected(self, engine):
        assert engine.fire("p1", -1, 0)["valid"] is False

    def test_negative_col_rejected(self, engine):
        assert engine.fire("p1", 0, -1)["valid"] is False


# ── Hit / miss detection ──────────────────────────────────────────────────────

class TestHitDetection:
    def test_hit_on_ship_cell(self, engine):
        result = engine.fire("p1", 0, 0)   # p2's carrier at row 0
        assert result["hit"] is True

    def test_miss_on_empty_cell(self, engine):
        result = engine.fire("p1", 1, 0)   # row 1 always empty
        assert result["hit"] is False

    def test_hit_does_not_immediately_sink_large_ship(self, engine):
        result = engine.fire("p1", 0, 0)   # first hit on carrier (size 5)
        assert result["sunk"] is False

    def test_sunk_reported_when_ship_destroyed(self, engine):
        # Sink p2's destroyer (row 8, cols 0-1) — need p2 to fire in between
        engine.fire("p1", 8, 0)
        engine.fire("p2", 1, 0)   # p2 miss
        result = engine.fire("p1", 8, 1)
        assert result["sunk"] is True
        assert result["ship_name"] == "destroyer"

    def test_sunk_ship_name_none_when_not_sunk(self, engine):
        result = engine.fire("p1", 0, 0)   # first hit on carrier
        assert result["ship_name"] is None

    def test_duplicate_shot_rejected(self, engine):
        engine.fire("p1", 9, 9)            # p1 fires at (9,9)
        engine.fire("p2", 9, 9)            # p2 fires at (9,9)
        result = engine.fire("p1", 9, 9)   # p1 fires same cell again → rejected
        assert result["valid"] is False


# ── Board view (DR-4 — no opponent ship positions) ────────────────────────────

class TestBoardView:
    def test_own_ships_visible(self, engine):
        view = engine.board_view_for("p1")
        assert len(view["your_ships"]) == 5

    def test_opponent_ships_never_in_view(self, engine):
        """DR-4: opponent ship positions must never appear in the view."""
        view = engine.board_view_for("p1")
        assert "opponent_ships" not in view

    def test_view_contains_only_allowed_keys(self, engine):
        view = engine.board_view_for("p1")
        allowed = {"your_ships", "shots_received", "shots_fired"}
        assert set(view.keys()) == allowed

    def test_shots_fired_at_opponent_recorded(self, engine):
        engine.fire("p1", 5, 5)
        engine.fire("p2", 1, 0)
        view = engine.board_view_for("p1")
        fired = {(s["row"], s["col"]) for s in view["shots_fired"]}
        assert (5, 5) in fired

    def test_shots_received_from_opponent_recorded(self, engine):
        engine.fire("p1", 9, 9)           # p1 fires, turn → p2
        engine.fire("p2", 0, 0)           # p2 hits p1's carrier
        view = engine.board_view_for("p1")
        received = {(s["row"], s["col"]) for s in view["shots_received"]}
        assert (0, 0) in received

    def test_p2_view_independent_of_p1_view(self, engine):
        engine.fire("p1", 5, 5)
        view_p1 = engine.board_view_for("p1")
        view_p2 = engine.board_view_for("p2")
        p1_fired = {(s["row"], s["col"]) for s in view_p1["shots_fired"]}
        p2_received = {(s["row"], s["col"]) for s in view_p2["shots_received"]}
        assert (5, 5) in p1_fired
        assert (5, 5) in p2_received


# ── Win condition ─────────────────────────────────────────────────────────────

class TestWinCondition:
    def test_winner_is_none_at_start(self, engine):
        assert engine.state.winner is None

    def test_winner_set_after_all_ships_sunk(self, engine):
        sink_all_p2(engine)
        assert engine.state.winner == "p1"

    def test_status_finished_after_win(self, engine):
        sink_all_p2(engine)
        assert engine.state.status == GameStatus.FINISHED

    def test_fire_rejected_after_game_over(self, engine):
        sink_all_p2(engine)
        result = engine.fire("p1", 9, 9)
        assert result["valid"] is False

    def test_next_turn_none_after_final_shot(self, engine):
        # Drive to one shot before the last, using unique p2 cells
        targets = [
            (0, 0), (0, 1), (0, 2), (0, 3), (0, 4),
            (2, 0), (2, 1), (2, 2), (2, 3),
            (4, 0), (4, 1), (4, 2),
            (6, 0), (6, 1), (6, 2),
            (8, 0),                     # penultimate — one cell of destroyer left
        ]
        p2_cells = [(1, c) for c in range(10)] + [(3, c) for c in range(10)]
        for i, (r, c) in enumerate(targets):
            engine.fire("p1", r, c)
            engine.fire("p2", *p2_cells[i])

        result = engine.fire("p1", 8, 1)   # final shot — sinks last ship
        assert result["winner"] == "p1"
        assert result["next_turn"] is None
