from app.engine import evaluate

PRICES = [100, 101, 100, 101, 100, 101, 100]  # ~1% daily wobble


def test_two_signals_flag_with_reasons():
    r = evaluate(PRICES + [103], [100, 110, 90, 100, 105, 220])
    assert r.flagged
    assert len(r.reasons) == 2
    assert r.confidence in ("medium", "high")


def test_single_signal_does_not_flag():
    # Big price move, but normal volume -> only one signal, so no flag.
    r = evaluate(PRICES + [120], [100, 110, 90, 100, 105, 108])
    assert not r.flagged
    assert r.reasons == []


def test_no_signals_does_not_flag():
    r = evaluate(PRICES + [101], [100, 110, 90, 100, 105, 108])
    assert not r.flagged


def test_moderate_co_occurrence_is_medium():
    r = evaluate(PRICES + [103], [100, 110, 90, 100, 105, 220])
    assert r.confidence == "medium"


def test_strong_co_occurrence_is_high():
    r = evaluate(PRICES + [120], [100, 110, 90, 100, 105, 320])
    assert r.confidence == "high"
