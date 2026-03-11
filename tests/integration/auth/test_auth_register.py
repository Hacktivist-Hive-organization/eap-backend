# tests/integration/auth/test_auth_register.py

from app.core.config import settings
from app.models.db_user import DbUser

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


def test_register_success(client):
    response = client.post(
        f"{API_PREFIX}/register",
        json=register_payload("test@example.com"),
    )

    assert response.status_code == 201

    body = response.json()

    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_register_existing_email(client):
    client.post(
        f"{API_PREFIX}/register",
        json=register_payload("existing@example.com"),
    )

    response = client.post(
        f"{API_PREFIX}/register",
        json=register_payload("existing@example.com"),
    )

    assert response.status_code == 409


def test_register_email_case_insensitive(client):
    response1 = client.post(
        f"{API_PREFIX}/register",
        json=register_payload("Test@Example.com"),
    )

    assert response1.status_code == 201

    response2 = client.post(
        f"{API_PREFIX}/register",
        json=register_payload("test@example.com"),
    )

    assert response2.status_code == 409


def test_register_weak_password(client):
    response = client.post(
        f"{API_PREFIX}/register",
        json=register_payload("weak@example.com", password="weak"),
    )

    assert response.status_code == 422


def test_register_without_email(client):
    response = client.post(
        f"{API_PREFIX}/register",
        json={
            "password": "StrongP@ss1",
            "first_name": "John",
            "last_name": "Doe",
        },
    )

    assert response.status_code == 422


def test_register_without_password(client):
    response = client.post(
        f"{API_PREFIX}/register",
        json={
            "email": "nopassword@example.com",
            "first_name": "John",
            "last_name": "Doe",
        },
    )

    assert response.status_code == 422


def test_register_without_first_name(client):
    response = client.post(
        f"{API_PREFIX}/register",
        json={
            "email": "nofirst@example.com",
            "password": "StrongP@ss1",
            "last_name": "Doe",
        },
    )

    assert response.status_code == 422


def test_register_without_last_name(client):
    response = client.post(
        f"{API_PREFIX}/register",
        json={
            "email": "nolast@example.com",
            "password": "StrongP@ss1",
            "first_name": "John",
        },
    )

    assert response.status_code == 422


def test_register_invalid_email(client):
    response = client.post(
        f"{API_PREFIX}/register",
        json=register_payload("not-an-email"),
    )

    assert response.status_code == 422


def test_register_email_with_spaces(client, db_session):
    response = client.post(
        f"{API_PREFIX}/register",
        json=register_payload("  spaced@example.com  "),
    )

    assert response.status_code == 201

    user = db_session.query(DbUser).filter_by(email="spaced@example.com").one()

    assert user.email == "spaced@example.com"


def test_email_saved_lowercase(client, db_session):
    client.post(
        f"{API_PREFIX}/register",
        json=register_payload("MiXeD@Example.com"),
    )

    user = db_session.query(DbUser).filter_by(email="mixed@example.com").one()

    assert user.email == "mixed@example.com"


def test_register_saves_first_and_last_name(client, db_session):
    client.post(
        f"{API_PREFIX}/register",
        json=register_payload(
            email="names@example.com",
            first_name="Alice",
            last_name="Smith",
        ),
    )

    user = db_session.query(DbUser).filter_by(email="names@example.com").one()

    assert user.first_name == "Alice"
    assert user.last_name == "Smith"


def test_user_is_active_by_default(client, db_session):
    client.post(
        f"{API_PREFIX}/register",
        json=register_payload("active@example.com"),
    )


def test_register_missing_fields(client):
    response = client.post(
        f"{API_PREFIX}/register",
        json={"password": "StrongP@ss1", "first_name": "John", "last_name": "Doe"},
    )
    assert response.status_code == 422

    response = client.post(
        f"{API_PREFIX}/register",
        json={
            "email": "nopassword@example.com",
            "first_name": "John",
            "last_name": "Doe",
        },
    )
    assert response.status_code == 422

    response = client.post(
        f"{API_PREFIX}/register",
        json={
            "email": "nofirst@example.com",
            "password": "StrongP@ss1",
            "last_name": "Doe",
        },
    )
    assert response.status_code == 422

    response = client.post(
        f"{API_PREFIX}/register",
        json={
            "email": "nolast@example.com",
            "password": "StrongP@ss1",
            "first_name": "John",
        },
    )
    assert response.status_code == 422
