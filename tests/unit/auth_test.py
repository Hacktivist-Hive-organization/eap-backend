# tests/api/v1/auth_test.py

from app.core.config import settings

API_PREFIX = f"{settings.API_V1_PREFIX}/auth"


def test_register_success(client):
    response = client.post(
        f"{API_PREFIX}/register",
        json={"email": "test@example.com", "password": "StrongP@ss1"},
    )
    assert response.status_code == 201


def test_register_existing_email(client):
    client.post(
        f"{API_PREFIX}/register",
        json={"email": "existing@example.com", "password": "StrongP@ss1"},
    )

    response = client.post(
        f"{API_PREFIX}/register",
        json={"email": "existing@example.com", "password": "StrongP@ss1"},
    )
    assert response.status_code == 409


def test_register_weak_password(client):
    response = client.post(
        f"{API_PREFIX}/register", json={"email": "weak@example.com", "password": "weak"}
    )
    assert response.status_code == 422


def test_login_success(client):
    client.post(
        f"{API_PREFIX}/register",
        json={"email": "login@example.com", "password": "StrongP@ss1"},
    )

    response = client.post(
        f"{API_PREFIX}/login",
        json={"email": "login@example.com", "password": "StrongP@ss1"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_email(client):
    response = client.post(
        f"{API_PREFIX}/login",
        json={"email": "wrong@example.com", "password": "StrongP@ss1"},
    )
    assert response.status_code == 401


def test_login_wrong_password(client):
    client.post(
        f"{API_PREFIX}/register",
        json={"email": "wrongpass@example.com", "password": "StrongP@ss1"},
    )

    response = client.post(
        f"{API_PREFIX}/login",
        json={"email": "wrongpass@example.com", "password": "WrongP@ss1"},
    )
    assert response.status_code == 401
git