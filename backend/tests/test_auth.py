def test_register_returns_token(client):
    r = client.post("/auth/register", json={"email": "a@b.com", "password": "pw123456"})
    assert r.status_code == 200
    assert r.json()["access_token"]


def test_duplicate_email_rejected(client):
    client.post("/auth/register", json={"email": "a@b.com", "password": "pw123456"})
    r = client.post("/auth/register", json={"email": "a@b.com", "password": "other123"})
    assert r.status_code == 409


def test_login_succeeds_with_correct_password(client):
    client.post("/auth/register", json={"email": "a@b.com", "password": "pw123456"})
    r = client.post("/auth/login", json={"email": "a@b.com", "password": "pw123456"})
    assert r.status_code == 200
    assert r.json()["access_token"]


def test_login_fails_with_wrong_password(client):
    client.post("/auth/register", json={"email": "a@b.com", "password": "pw123456"})
    r = client.post("/auth/login", json={"email": "a@b.com", "password": "wrongpw12"})
    assert r.status_code == 401


def test_me_requires_valid_token(client):
    assert client.get("/me").status_code == 401
    assert client.get("/me", headers={"Authorization": "Bearer nonsense"}).status_code == 401


def test_me_returns_current_user(client):
    token = client.post(
        "/auth/register", json={"email": "a@b.com", "password": "pw123456"}
    ).json()["access_token"]
    r = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == "a@b.com"
