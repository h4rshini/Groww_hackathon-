import pytest

import app.watchlist as watchlist


@pytest.fixture(autouse=True)
def no_network_backfill(monkeypatch):
    # Don't hit the vendor in unit tests; the backfill path is covered separately.
    monkeypatch.setattr(watchlist, "backfill_symbol", lambda symbol: None)


def test_watchlist_requires_auth(client):
    assert client.get("/watchlist").status_code == 401


def test_empty_watchlist(client, auth_headers):
    r = client.get("/watchlist", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == []


def test_add_ticker_returns_immediately(client, auth_headers):
    r = client.post("/watchlist", json={"symbol": "aapl"}, headers=auth_headers)
    assert r.status_code == 201
    body = r.json()
    assert body["symbol"] == "AAPL"          # normalized to upper
    assert body["latest_close"] is None       # data not fetched yet


def test_add_then_list(client, auth_headers):
    client.post("/watchlist", json={"symbol": "MSFT"}, headers=auth_headers)
    symbols = [i["symbol"] for i in client.get("/watchlist", headers=auth_headers).json()]
    assert symbols == ["MSFT"]


def test_duplicate_add_rejected(client, auth_headers):
    client.post("/watchlist", json={"symbol": "AAPL"}, headers=auth_headers)
    r = client.post("/watchlist", json={"symbol": "AAPL"}, headers=auth_headers)
    assert r.status_code == 409


def test_remove_ticker(client, auth_headers):
    client.post("/watchlist", json={"symbol": "AAPL"}, headers=auth_headers)
    assert client.delete("/watchlist/AAPL", headers=auth_headers).status_code == 204
    assert client.get("/watchlist", headers=auth_headers).json() == []


def test_remove_missing_ticker(client, auth_headers):
    assert client.delete("/watchlist/AAPL", headers=auth_headers).status_code == 404


def test_watchlists_are_per_user(client, auth_headers):
    client.post("/watchlist", json={"symbol": "AAPL"}, headers=auth_headers)
    other = client.post(
        "/auth/register", json={"email": "other@e.com", "password": "pw123456"}
    ).json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other}"}
    assert client.get("/watchlist", headers=other_headers).json() == []
