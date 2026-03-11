# tests/integration/auth/test_auth_email_verification.py

from app.common.security import create_access_token
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


def test_register_requires_email_verification(client, db_session, monkeypatch):
    monkeypatch.setattr(settings, "EMAIL_VERIFICATION_REQUIRED", True)

    response = client.post(
        f"{API_PREFIX}/register",
        json=register_payload("verify@example.com"),
    )

    assert response.status_code == 201

    user = db_session.query(DbUser).filter_by(email="verify@example.com").one()

    assert user.is_email_verified is False


def test_verify_email_updates_user(client, db_session, monkeypatch):
    monkeypatch.setattr(settings, "EMAIL_VERIFICATION_REQUIRED", True)

    client.post(
        f"{API_PREFIX}/register",
        json=register_payload("confirm@example.com"),
    )

    user = db_session.query(DbUser).filter_by(email="confirm@example.com").one()

    token = create_access_token({"sub": str(user.id), "type": "email_verification"})

    response = client.get(
        f"{API_PREFIX}/verify-email",
        params={"token": token},
    )

    assert response.status_code == 200

    db_session.refresh(user)

    assert user.is_active is True
    assert user.is_email_verified is True


def test_verify_email_invalid_token_type(client, db_session, monkeypatch):
    monkeypatch.setattr(settings, "EMAIL_VERIFICATION_REQUIRED", True)

    client.post(
        f"{API_PREFIX}/register",
        json=register_payload("wrongtoken@example.com"),
    )

    user = db_session.query(DbUser).filter_by(email="wrongtoken@example.com").one()

    token = create_access_token({"sub": str(user.id), "type": "password_reset"})

    response = client.get(
        f"{API_PREFIX}/verify-email",
        params={"token": token},
    )

    assert response.status_code == 401


def test_verify_email_user_not_found(client):
    token = create_access_token({"sub": "999999", "type": "email_verification"})

    response = client.get(
        f"{API_PREFIX}/verify-email",
        params={"token": token},
    )

    assert response.status_code == 404
