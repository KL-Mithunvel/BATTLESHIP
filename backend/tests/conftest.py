import pytest
from app.game.board import Board
from app.game.engine import GameEngine
from app.game.player import Player
from app.game.rules import build_ships

# Standard fleet placement used across all test modules.
# Rows 0,2,4,6,8 contain ships — rows 1,3,5,7,9 are always empty.
STANDARD_PLACEMENTS = [
    {"name": "carrier",    "row": 0, "col": 0, "horizontal": True},
    {"name": "battleship", "row": 2, "col": 0, "horizontal": True},
    {"name": "cruiser",    "row": 4, "col": 0, "horizontal": True},
    {"name": "submarine",  "row": 6, "col": 0, "horizontal": True},
    {"name": "destroyer",  "row": 8, "col": 0, "horizontal": True},
]


def place_fleet(player: Player, placements: list[dict] = STANDARD_PLACEMENTS) -> None:
    """Place a full fleet on a player's board."""
    ships = build_ships(placements)
    for p, ship in zip(placements, ships):
        ok = player.board.place_ship(ship, p["row"], p["col"], p["horizontal"])
        assert ok, f"Fixture failed to place {ship.name} at ({p['row']},{p['col']})"
    player.ships_placed = True


def make_engine(p1_id="p1", p2_id="p2") -> GameEngine:
    """Return a fully-initialised engine with both fleets placed."""
    p1 = Player(p1_id, "Alice")
    p2 = Player(p2_id, "Bob")
    place_fleet(p1)
    place_fleet(p2)
    return GameEngine(p1, p2)


def sink_all_p2(engine: GameEngine) -> None:
    """Drive p1 to sink every one of p2's ships. p2 fires unique misses in between."""
    targets = [
        (0, 0), (0, 1), (0, 2), (0, 3), (0, 4),  # carrier     (5)
        (2, 0), (2, 1), (2, 2), (2, 3),            # battleship  (4)
        (4, 0), (4, 1), (4, 2),                    # cruiser     (3)
        (6, 0), (6, 1), (6, 2),                    # submarine   (3)
        (8, 0), (8, 1),                            # destroyer   (2)
    ]
    # 20 unique empty cells for p2 to fire at (rows 1 and 3 are always empty)
    p2_cells = [(1, c) for c in range(10)] + [(3, c) for c in range(10)]
    for i, (r, c) in enumerate(targets):
        engine.fire("p1", r, c)
        if engine.state.winner:
            break
        engine.fire("p2", *p2_cells[i])


@pytest.fixture
def engine():
    return make_engine()
