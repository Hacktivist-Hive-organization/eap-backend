# test_auth_login.py

from app.core.config import settings

API_PREFIX = f"{settings.API_V1_PREFIX}/auth"


def register_payload(
    email: str,
    password: str = "StrongP@ss1",
    first_name: str = "John",
    last_name: str = "Doe",
):
    return {
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
    }


def test_login_success(client):
    client.post(
        f"{API_PREFIX}/register",
        json=register_payload("login@example.com"),
    )

    response = client.post(
        f"{API_PREFIX}/login",
        json={
            "email": "login@example.com",
            "password": "StrongP@ss1",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_wrong_email(client):
    response = client.post(
        f"{API_PREFIX}/login",
        json={
            "email": "wrong@example.com",
            "password": "StrongP@ss1",
        },
    )

    assert response.status_code == 401


def test_login_wrong_password(client):
    client.post(
        f"{API_PREFIX}/register",
        json=register_payload("wrongpass@example.com"),
    )

    response = client.post(
        f"{API_PREFIX}/login",
        json={
            "email": "wrongpass@example.com",
            "password": "WrongP@ss1",
        },
    )

    assert response.status_code == 401


def test_login_email_case_insensitive(client):
    client.post(
        f"{API_PREFIX}/register",
        json=register_payload("User@Example.com"),
    )

    response = client.post(
        f"{API_PREFIX}/login",
        json={
            "email": "user@example.com",
            "password": "StrongP@ss1",
        },
    )

    assert response.status_code == 200


def test_login_invalid_email_format(client):
    response = client.post(
        f"{API_PREFIX}/login",
        json={
            "email": "not-an-email",
            "password": "StrongP@ss1",
        },
    )

    assert response.status_code == 422


def test_login_email_with_spaces(client):
    client.post(
        f"{API_PREFIX}/register",
        json=register_payload("trimlogin@example.com"),
    )

    response = client.post(
        f"{API_PREFIX}/login",
        json={
            "email": "  trimlogin@example.com  ",
            "password": "StrongP@ss1",
        },
    )

    assert response.status_code == 200
