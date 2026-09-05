import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.watchlist as watchlist
from app.db import Base
from app.deps import get_db
from app.main import app


@pytest.fixture
def engine(tmp_path):
    eng = create_engine(
        f"sqlite:///{tmp_path}/test.db",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(eng)
    return eng


@pytest.fixture
def _session_factory(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture
def client(_session_factory):
    def override_get_db():
        db = _session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def db(_session_factory):
    s = _session_factory()
    yield s
    s.close()


@pytest.fixture
def auth_headers(client):
    token = client.post(
        "/auth/register", json={"email": "u@e.com", "password": "pw123456"}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def no_network_backfill(monkeypatch):
    # Never call the market data provider from tests.
    monkeypatch.setattr(watchlist, "backfill_symbol", lambda symbol: None)
