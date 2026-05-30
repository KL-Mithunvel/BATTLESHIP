from typing import Optional
from .ship import Ship

BOARD_SIZE = 10


class Board:
    def __init__(self) -> None:
        self._grid: list[list[Optional[Ship]]] = [
            [None] * BOARD_SIZE for _ in range(BOARD_SIZE)
        ]
        self._shots: set[tuple[int, int]] = set()
        self.ships: list[Ship] = []

    def place_ship(self, ship: Ship, row: int, col: int, horizontal: bool) -> bool:
        cells: list[tuple[int, int]] = []
        for i in range(ship.size):
            r = row if horizontal else row + i
            c = col + i if horizontal else col
            if not (0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE):
                return False
            if self._grid[r][c] is not None:
                return False
            cells.append((r, c))

        ship.cells = cells
        for r, c in cells:
            self._grid[r][c] = ship
        self.ships.append(ship)
        return True

    def receive_shot(self, row: int, col: int) -> dict:
        if (row, col) in self._shots:
            return {"valid": False, "reason": "Already shot here"}
        self._shots.add((row, col))
        ship = self._grid[row][col]
        if ship:
            ship.register_hit()
            return {
                "valid": True,
                "hit": True,
                "sunk": ship.is_sunk,
                "ship_name": ship.name if ship.is_sunk else None,
            }
        return {"valid": True, "hit": False, "sunk": False, "ship_name": None}

    @property
    def all_sunk(self) -> bool:
        return bool(self.ships) and all(s.is_sunk for s in self.ships)

    def shots_received(self) -> list[dict]:
        return [
            {
                "row": r,
                "col": c,
                "hit": self._grid[r][c] is not None,
                "sunk": self._grid[r][c].is_sunk if self._grid[r][c] else False,
            }
            for r, c in self._shots
        ]
