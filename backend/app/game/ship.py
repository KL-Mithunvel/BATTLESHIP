from dataclasses import dataclass, field
from typing import List, Tuple

SHIP_TYPES: dict[str, int] = {
    "carrier": 5,
    "battleship": 4,
    "cruiser": 3,
    "submarine": 3,
    "destroyer": 2,
}

REQUIRED_FLEET: list[str] = ["carrier", "battleship", "cruiser", "submarine", "destroyer"]


@dataclass
class Ship:
    name: str
    size: int
    cells: List[Tuple[int, int]] = field(default_factory=list)
    hits: int = 0

    @property
    def is_sunk(self) -> bool:
        return self.hits >= self.size

    def register_hit(self) -> None:
        self.hits += 1
