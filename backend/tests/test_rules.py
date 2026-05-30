import pytest
from app.game.rules import validate_username, validate_placements, build_ships
from app.game.ship import SHIP_TYPES

VALID_FLEET = [
    {"name": "carrier",    "row": 0, "col": 0, "horizontal": True},
    {"name": "battleship", "row": 2, "col": 0, "horizontal": True},
    {"name": "cruiser",    "row": 4, "col": 0, "horizontal": True},
    {"name": "submarine",  "row": 6, "col": 0, "horizontal": True},
    {"name": "destroyer",  "row": 8, "col": 0, "horizontal": True},
]


# ── Username validation (DR-5) ────────────────────────────────────────────────

class TestValidateUsername:
    def test_valid_simple_name(self):
        ok, result = validate_username("Alice")
        assert ok
        assert result == "Alice"

    def test_valid_name_with_numbers(self):
        ok, result = validate_username("Player1")
        assert ok
        assert result == "Player1"

    def test_valid_name_with_space(self):
        ok, result = validate_username("Player One")
        assert ok

    def test_strips_surrounding_whitespace(self):
        ok, result = validate_username("  Bob  ")
        assert ok
        assert result == "Bob"

    def test_exactly_20_chars_accepted(self):
        ok, _ = validate_username("A" * 20)
        assert ok

    def test_21_chars_rejected(self):
        ok, _ = validate_username("A" * 21)
        assert not ok

    def test_empty_string_rejected(self):
        ok, _ = validate_username("")
        assert not ok

    def test_whitespace_only_rejected(self):
        ok, _ = validate_username("   ")
        assert not ok

    def test_special_chars_rejected(self):
        ok, _ = validate_username("hack<script>")
        assert not ok

    def test_unicode_rejected(self):
        ok, _ = validate_username("Ünïcödé")
        assert not ok

    def test_sql_injection_attempt_rejected(self):
        ok, _ = validate_username("'; DROP TABLE--")
        assert not ok

    def test_single_char_accepted(self):
        ok, result = validate_username("X")
        assert ok
        assert result == "X"


# ── Placement validation ──────────────────────────────────────────────────────

class TestValidatePlacements:
    def test_valid_full_fleet(self):
        ok, msg = validate_placements(VALID_FLEET)
        assert ok
        assert msg == ""

    def test_empty_list_rejected(self):
        ok, _ = validate_placements([])
        assert not ok

    def test_too_few_ships_rejected(self):
        ok, _ = validate_placements(VALID_FLEET[:3])
        assert not ok

    def test_too_many_ships_rejected(self):
        extra = VALID_FLEET + [{"name": "destroyer", "row": 9, "col": 0, "horizontal": True}]
        ok, _ = validate_placements(extra)
        assert not ok

    def test_duplicate_ship_type_rejected(self):
        dupes = [p for p in VALID_FLEET if p["name"] != "destroyer"]
        dupes.append({"name": "carrier", "row": 9, "col": 0, "horizontal": True})
        ok, msg = validate_placements(dupes)
        assert not ok

    def test_missing_ship_type_rejected(self):
        without_destroyer = [p for p in VALID_FLEET if p["name"] != "destroyer"]
        without_destroyer.append({"name": "carrier", "row": 9, "col": 0, "horizontal": True})
        ok, _ = validate_placements(without_destroyer)
        assert not ok


# ── build_ships ───────────────────────────────────────────────────────────────

class TestBuildShips:
    def test_correct_number_of_ships(self):
        ships = build_ships(VALID_FLEET)
        assert len(ships) == 5

    def test_ship_sizes_match_types(self):
        ships = build_ships(VALID_FLEET)
        for ship in ships:
            assert ship.size == SHIP_TYPES[ship.name]

    def test_ships_start_undamaged(self):
        ships = build_ships(VALID_FLEET)
        assert all(s.hits == 0 for s in ships)
        assert all(not s.is_sunk for s in ships)
