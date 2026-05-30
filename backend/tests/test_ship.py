from app.game.ship import Ship


def test_new_ship_has_no_hits():
    ship = Ship("destroyer", 2)
    assert ship.hits == 0


def test_new_ship_is_not_sunk():
    ship = Ship("destroyer", 2)
    assert not ship.is_sunk


def test_one_hit_does_not_sink_large_ship():
    ship = Ship("carrier", 5)
    ship.register_hit()
    assert not ship.is_sunk


def test_hits_accumulate():
    ship = Ship("battleship", 4)
    for expected in range(1, 5):
        ship.register_hit()
        assert ship.hits == expected


def test_ship_sunk_when_hits_equal_size():
    ship = Ship("destroyer", 2)
    ship.register_hit()
    ship.register_hit()
    assert ship.is_sunk


def test_ship_not_sunk_one_hit_before_max():
    ship = Ship("cruiser", 3)
    ship.register_hit()
    ship.register_hit()
    assert not ship.is_sunk


def test_submarine_sinks_at_three_hits():
    ship = Ship("submarine", 3)
    for _ in range(3):
        ship.register_hit()
    assert ship.is_sunk
