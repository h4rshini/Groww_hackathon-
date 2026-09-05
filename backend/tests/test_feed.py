from datetime import date, timedelta

from app.models import ChangeEvent, Instrument, Observation


def _add_watched(client, db, auth_headers, symbol="AAPL"):
    client.post("/watchlist", json={"symbol": symbol}, headers=auth_headers)
    return db.query(Instrument).filter_by(symbol=symbol).first()


def _seed_event(db, inst, days_ago=1, score=5.0, confidence="high", close=100.0):
    d = date.today() - timedelta(days=days_ago)
    db.add(Observation(instrument_id=inst.id, bar_date=d, open=close, high=close,
                       low=close, close=close, volume=1000))
    db.add(ChangeEvent(instrument_id=inst.id, window_start=d - timedelta(days=20),
                       window_end=d, confidence=confidence, score=score,
                       reasons=["Price moved up 3.0x its typical daily range",
                                "Volume was 2.4x its recent average"]))
    db.commit()


def test_feed_requires_auth(client):
    assert client.get("/feed").status_code == 401


def test_feed_empty_without_events(client, auth_headers, db):
    _add_watched(client, db, auth_headers)
    r = client.get("/feed", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["items"] == []


def test_feed_shows_flagged_stock_with_reasons(client, auth_headers, db):
    inst = _add_watched(client, db, auth_headers)
    _seed_event(db, inst)
    items = client.get("/feed", headers=auth_headers).json()["items"]
    assert len(items) == 1
    assert items[0]["symbol"] == "AAPL"
    assert len(items[0]["reasons"]) == 2


def test_feed_ranked_by_score(client, auth_headers, db):
    a = _add_watched(client, db, auth_headers, "AAPL")
    b = _add_watched(client, db, auth_headers, "MSFT")
    _seed_event(db, a, score=3.0)
    _seed_event(db, b, score=9.0)
    items = client.get("/feed", headers=auth_headers).json()["items"]
    assert [i["symbol"] for i in items] == ["MSFT", "AAPL"]


def test_feed_caps_old_events_for_new_user(client, auth_headers, db):
    inst = _add_watched(client, db, auth_headers)
    _seed_event(db, inst, days_ago=40)  # older than the 30-day cap
    assert client.get("/feed", headers=auth_headers).json()["items"] == []


def test_feed_window_shrinks_after_marking_seen(client, auth_headers, db):
    inst = _add_watched(client, db, auth_headers)
    _seed_event(db, inst, days_ago=1)
    assert len(client.get("/feed", headers=auth_headers).json()["items"]) == 1
    client.post("/seen", headers=auth_headers)
    # last_seen is now ~today, so yesterday's flag is no longer "since you looked".
    assert client.get("/feed", headers=auth_headers).json()["items"] == []
