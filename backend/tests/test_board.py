import pytest
from app.game.board import Board
from app.game.ship import Ship


def ship(name, size):
    return Ship(name, size)


# ── Placement ────────────────────────────────────────────────────────────────

class TestPlaceShip:
    def test_horizontal_sets_correct_cells(self):
        b = Board()
        s = ship("destroyer", 2)
        assert b.place_ship(s, 0, 0, horizontal=True)
        assert s.cells == [(0, 0), (0, 1)]

    def test_vertical_sets_correct_cells(self):
        b = Board()
        s = ship("cruiser", 3)
        assert b.place_ship(s, 0, 0, horizontal=False)
        assert s.cells == [(0, 0), (1, 0), (2, 0)]

    def test_ship_added_to_ships_list(self):
        b = Board()
        s = ship("destroyer", 2)
        b.place_ship(s, 0, 0, horizontal=True)
        assert s in b.ships

    def test_place_at_bottom_right_boundary(self):
        b = Board()
        s = ship("destroyer", 2)
        assert b.place_ship(s, 9, 8, horizontal=True)

    def test_horizontal_overflows_right_boundary(self):
        b = Board()
        s = ship("destroyer", 2)
        assert not b.place_ship(s, 0, 9, horizontal=True)

    def test_vertical_overflows_bottom_boundary(self):
        b = Board()
        s = ship("destroyer", 2)
        assert not b.place_ship(s, 9, 0, horizontal=False)

    def test_carrier_exactly_fits_horizontally(self):
        b = Board()
        s = ship("carrier", 5)
        assert b.place_ship(s, 0, 5, horizontal=True)   # cols 5-9

    def test_carrier_overflows_by_one(self):
        b = Board()
        s = ship("carrier", 5)
        assert not b.place_ship(s, 0, 6, horizontal=True)  # cols 6-10: invalid

    def test_overlap_rejected(self):
        b = Board()
        b.place_ship(ship("destroyer", 2), 0, 0, horizontal=True)
        assert not b.place_ship(ship("cruiser", 3), 0, 0, horizontal=True)

    def test_partial_overlap_rejected(self):
        b = Board()
        b.place_ship(ship("destroyer", 2), 0, 2, horizontal=True)   # (0,2),(0,3)
        assert not b.place_ship(ship("cruiser", 3), 0, 1, horizontal=True)  # (0,1),(0,2),(0,3)

    def test_adjacent_ships_allowed(self):
        """Standard Battleship rules permit ships to touch."""
        b = Board()
        b.place_ship(ship("destroyer", 2), 0, 0, horizontal=True)
        assert b.place_ship(ship("destroyer", 2), 1, 0, horizontal=True)

    def test_failed_placement_does_not_modify_board(self):
        b = Board()
        b.place_ship(ship("destroyer", 2), 0, 0, horizontal=True)
        b.place_ship(ship("cruiser", 3), 0, 0, horizontal=True)  # fails
        assert len(b.ships) == 1


# ── Shot handling ─────────────────────────────────────────────────────────────

class TestReceiveShot:
    def test_miss_on_empty_cell(self):
        b = Board()
        r = b.receive_shot(5, 5)
        assert r["valid"] is True
        assert r["hit"] is False
        assert r["sunk"] is False

    def test_hit_on_ship_cell(self):
        b = Board()
        b.place_ship(ship("destroyer", 2), 3, 3, horizontal=True)
        r = b.receive_shot(3, 3)
        assert r["valid"] is True
        assert r["hit"] is True
        assert r["sunk"] is False

    def test_sunk_when_all_cells_hit(self):
        b = Board()
        b.place_ship(ship("destroyer", 2), 3, 3, horizontal=True)
        b.receive_shot(3, 3)
        r = b.receive_shot(3, 4)
        assert r["sunk"] is True
        assert r["ship_name"] == "destroyer"

    def test_ship_name_none_when_not_sunk(self):
        b = Board()
        b.place_ship(ship("battleship", 4), 0, 0, horizontal=True)
        r = b.receive_shot(0, 0)
        assert r["ship_name"] is None

    def test_duplicate_shot_rejected(self):
        b = Board()
        b.receive_shot(0, 0)
        r = b.receive_shot(0, 0)
        assert r["valid"] is False

    def test_duplicate_shot_on_ship_rejected(self):
        b = Board()
        b.place_ship(ship("destroyer", 2), 0, 0, horizontal=True)
        b.receive_shot(0, 0)
        r = b.receive_shot(0, 0)
        assert r["valid"] is False

    def test_shots_received_tracks_all_shots(self):
        b = Board()
        b.receive_shot(1, 2)
        b.receive_shot(3, 4)
        coords = {(s["row"], s["col"]) for s in b.shots_received()}
        assert (1, 2) in coords
        assert (3, 4) in coords


# ── all_sunk ──────────────────────────────────────────────────────────────────

class TestAllSunk:
    def test_empty_board_is_not_all_sunk(self):
        assert not Board().all_sunk

    def test_all_sunk_single_ship(self):
        b = Board()
        b.place_ship(ship("destroyer", 2), 0, 0, horizontal=True)
        b.receive_shot(0, 0)
        b.receive_shot(0, 1)
        assert b.all_sunk

    def test_not_all_sunk_with_one_surviving_ship(self):
        b = Board()
        b.place_ship(ship("destroyer", 2), 0, 0, horizontal=True)
        b.place_ship(ship("cruiser", 3),   2, 0, horizontal=True)
        b.receive_shot(0, 0)
        b.receive_shot(0, 1)  # destroyer sunk
        assert not b.all_sunk  # cruiser still alive

    def test_all_sunk_multiple_ships(self):
        b = Board()
        b.place_ship(ship("destroyer", 2), 0, 0, horizontal=True)
        b.place_ship(ship("cruiser", 3),   2, 0, horizontal=True)
        for r, c in [(0, 0), (0, 1), (2, 0), (2, 1), (2, 2)]:
            b.receive_shot(r, c)
        assert b.all_sunk
