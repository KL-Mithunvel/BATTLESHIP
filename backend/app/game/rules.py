import re
from .ship import Ship, SHIP_TYPES, REQUIRED_FLEET

# DR-5: username must be 1-20 chars, letters/numbers/spaces only
_USERNAME_RE = re.compile(r'^[A-Za-z0-9 ]{1,20}$')


def validate_username(raw: str) -> tuple[bool, str]:
    username = raw.strip()
    if not username:
        return False, "Username cannot be empty"
    if not _USERNAME_RE.match(username):
        return False, "Username must be 1-20 characters: letters, numbers, and spaces only"
    return True, username


def validate_placements(placements: list[dict]) -> tuple[bool, str]:
    if len(placements) != len(REQUIRED_FLEET):
        return False, f"Expected {len(REQUIRED_FLEET)} ships, got {len(placements)}"
    names = [p.get("name") for p in placements]
    for required in REQUIRED_FLEET:
        if names.count(required) != 1:
            return False, f"Fleet must contain exactly one {required}"
    return True, ""


def build_ships(placements: list[dict]) -> list[Ship]:
    return [Ship(name=p["name"], size=SHIP_TYPES[p["name"]]) for p in placements]
