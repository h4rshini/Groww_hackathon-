from app.signals import index_relative_signal, price_move_signal, volume_signal

# ~1% daily wobble, so a big final move stands out against it.
QUIET_PRICES = [100, 101, 100, 101, 100, 101, 100]


def test_price_fires_on_upward_spike():
    r = price_move_signal(QUIET_PRICES + [115])
    assert r.fired
    assert "up" in r.reason


def test_price_fires_on_downward_spike():
    r = price_move_signal(QUIET_PRICES + [85])
    assert r.fired
    assert "down" in r.reason


def test_price_quiet_day_does_not_fire():
    r = price_move_signal(QUIET_PRICES + [101])
    assert not r.fired


def test_price_needs_enough_history():
    r = price_move_signal([100, 101, 102])
    assert not r.fired


def test_price_flat_history_does_not_divide_by_zero():
    r = price_move_signal([100, 100, 100, 100, 100, 100, 110])
    assert not r.fired


QUIET_VOLUME = [100, 110, 90, 100, 105]


def test_volume_fires_on_spike():
    r = volume_signal(QUIET_VOLUME + [300])
    assert r.fired
    assert "average" in r.reason


def test_volume_normal_day_does_not_fire():
    r = volume_signal(QUIET_VOLUME + [108])
    assert not r.fired


def test_volume_needs_enough_history():
    r = volume_signal([100, 110])
    assert not r.fired


def test_volume_zero_average_does_not_divide_by_zero():
    r = volume_signal([0, 0, 0, 0, 0, 300])
    assert not r.fired


def test_index_signal_fires_when_stock_moves_but_market_flat():
    r = index_relative_signal(QUIET_PRICES + [103], index_return=0.0)
    assert r.fired
    assert "market" in r.reason


def test_index_signal_suppressed_when_move_matches_market():
    # ~3% up, but the market was also up ~3% — the move is explained by the market.
    r = index_relative_signal(QUIET_PRICES + [103], index_return=0.03)
    assert not r.fired


def test_index_signal_needs_market_data():
    r = index_relative_signal(QUIET_PRICES + [103], index_return=None)
    assert not r.fired
