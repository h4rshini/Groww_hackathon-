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


def test_all_three_signals_flag_high_with_three_reasons():
    r = evaluate(PRICES + [120], [100, 110, 90, 100, 105, 320], index_return=0.0)
    assert r.flagged
    assert len(r.reasons) == 3
    assert r.confidence == "high"


def test_index_signal_alone_does_not_flag():
    # A ~1.8% move trips the index signal (>1.5 sigma) but not price (<2 sigma),
    # and volume is normal -> only one signal, so no flag.
    r = evaluate(PRICES + [101.8], [100, 110, 90, 100, 105, 100], index_return=0.0)
    assert not r.flagged
