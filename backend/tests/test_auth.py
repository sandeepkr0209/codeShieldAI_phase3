"""
Authentication and authorization tests. Uses anon_client (no
pre-authenticated user) since these tests are about auth itself.
"""


def _register(client, email="alice@example.com", password="correct-horse-battery-staple", name="Alice"):
    return client.post(
        "/api/auth/register",
        json={"name": name, "email": email, "password": password, "confirm_password": password},
    )


def test_register_creates_user_and_sets_cookies(anon_client):
    response = _register(anon_client)
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "alice@example.com"
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies


def test_register_rejects_password_mismatch(anon_client):
    response = anon_client.post(
        "/api/auth/register",
        json={
            "name": "Alice",
            "email": "alice@example.com",
            "password": "correct-horse-battery-staple",
            "confirm_password": "different-password",
        },
    )
    assert response.status_code == 422


def test_register_rejects_short_password(anon_client):
    response = anon_client.post(
        "/api/auth/register",
        json={"name": "Alice", "email": "alice@example.com", "password": "short", "confirm_password": "short"},
    )
    assert response.status_code == 422


def test_register_rejects_duplicate_email(anon_client):
    _register(anon_client)
    response = _register(anon_client)
    assert response.status_code == 409


def test_me_requires_authentication(anon_client):
    response = anon_client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_returns_current_user_after_login(anon_client):
    _register(anon_client)
    response = anon_client.get("/api/auth/me")
    assert response.status_code == 200
    assert response.json()["email"] == "alice@example.com"


def test_login_with_correct_credentials(anon_client):
    _register(anon_client, email="bob@example.com", password="another-strong-password")
    anon_client.post("/api/auth/logout")
    response = anon_client.post(
        "/api/auth/login", json={"email": "bob@example.com", "password": "another-strong-password"}
    )
    assert response.status_code == 200


def test_login_with_wrong_password_fails(anon_client):
    _register(anon_client, email="carol@example.com", password="the-real-password")
    anon_client.post("/api/auth/logout")
    response = anon_client.post("/api/auth/login", json={"email": "carol@example.com", "password": "wrong-password"})
    assert response.status_code == 401


def test_logout_clears_session(anon_client):
    _register(anon_client)
    anon_client.post("/api/auth/logout")
    response = anon_client.get("/api/auth/me")
    assert response.status_code == 401


def test_change_password_requires_correct_current_password(anon_client):
    _register(anon_client, password="original-password-123")
    response = anon_client.post(
        "/api/auth/change-password",
        json={"current_password": "wrong-current-password", "new_password": "new-password-123"},
    )
    assert response.status_code == 401


def test_change_password_succeeds_and_new_password_works(anon_client):
    _register(anon_client, email="dave@example.com", password="original-password-123")
    response = anon_client.post(
        "/api/auth/change-password",
        json={"current_password": "original-password-123", "new_password": "brand-new-password-456"},
    )
    assert response.status_code == 204

    anon_client.post("/api/auth/logout")
    login = anon_client.post(
        "/api/auth/login", json={"email": "dave@example.com", "password": "brand-new-password-456"}
    )
    assert login.status_code == 200


def test_projects_require_authentication(anon_client):
    response = anon_client.get("/api/projects")
    assert response.status_code == 401
