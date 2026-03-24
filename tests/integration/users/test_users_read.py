# tests/integration/users/test_users_read.py

import pytest

from app.common.enums import UserRole
from app.common.security import hash_password
from app.core.config import settings
from app.models.db_user import DbUser

API_PREFIX = f"{settings.API_V1_PREFIX}/users"
AUTH_PREFIX = f"{settings.API_V1_PREFIX}/auth"


@pytest.fixture
def user_headers(client):
    def _create(email: str):
        client.post(
            f"{AUTH_PREFIX}/register",
            json={
                "email": email,
                "password": "StrongP@ss1",
                "first_name": "John",
                "last_name": "Doe",
            },
        )
        response = client.post(
            f"{AUTH_PREFIX}/login",
            json={"email": email, "password": "StrongP@ss1"},
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _create


@pytest.fixture
def admin_headers(client, db_session):
    def _create(email: str = "admin@example.com"):
        admin = DbUser(
            email=email,
            hashed_password=hash_password("StrongP@ss1"),
            first_name="Admin",
            last_name="User",
            role=UserRole.ADMIN,
            is_active=True,
        )
        db_session.add(admin)
        db_session.commit()
        db_session.refresh(admin)
        response = client.post(
            f"{AUTH_PREFIX}/login",
            json={"email": email, "password": "StrongP@ss1"},
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _create


@pytest.fixture
def create_user_direct(db_session):
    def _create(email: str, role: UserRole):
        user = DbUser(
            email=email,
            hashed_password=hash_password("StrongP@ss1"),
            first_name="Jane",
            last_name="Doe",
            role=role,
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _create


def test_get_me(client, user_headers):
    headers = user_headers("me@example.com")
    response = client.get(f"{API_PREFIX}/me", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "me@example.com"


def test_get_all_users_as_admin(client, admin_headers, create_user_direct, db_session):
    create_user_direct("user@example.com", UserRole.REQUESTER)
    headers = admin_headers()
    response = client.get(f"{API_PREFIX}/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) >= 2


def test_get_all_users_as_non_admin(client, user_headers):
    headers = user_headers("single@example.com")
    response = client.get(f"{API_PREFIX}/", headers=headers)
    assert response.status_code == 403
    assert len(response.json()) == 1


def test_get_user_by_id_self(client, user_headers, db_session):
    headers = user_headers("selfid@example.com")
    user = db_session.query(DbUser).filter_by(email="selfid@example.com").one()
    response = client.get(f"{API_PREFIX}/{user.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == user.id


def test_get_user_by_id_forbidden(client, user_headers, create_user_direct, db_session):
    headers = user_headers("user1@example.com")
    other = create_user_direct("user2@example.com", UserRole.REQUESTER)
    response = client.get(f"{API_PREFIX}/{other.id}", headers=headers)
    assert response.status_code == 403


def test_get_nonexistent_user_by_id_returns_403(client, user_headers):
    headers = user_headers("ghost@example.com")
    response = client.get(f"{API_PREFIX}/999999", headers=headers)
    assert response.status_code == 403


def test_admin_can_get_any_user_by_id(client, admin_headers, create_user_direct):
    headers = admin_headers()
    user = create_user_direct("user_any@example.com", UserRole.REQUESTER)
    response = client.get(f"{API_PREFIX}/{user.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == user.id


def test_get_user_without_token_returns_401(client, create_user_direct):
    user = create_user_direct("user_no_token@example.com", UserRole.REQUESTER)
    response = client.get(f"{API_PREFIX}/{user.id}")
    assert response.status_code == 401


def test_get_users_list_without_token_returns_401(client):
    response = client.get(f"{API_PREFIX}/")
    assert response.status_code == 401


def test_get_inactive_user_by_admin(
    client, admin_headers, create_user_direct, db_session
):
    headers = admin_headers()
    inactive_user = create_user_direct("inactive@example.com", UserRole.REQUESTER)
    inactive_user.is_active = False
    db_session.commit()
    response = client.get(f"{API_PREFIX}/{inactive_user.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == inactive_user.id


def test_get_inactive_user_by_non_admin(
    client, user_headers, create_user_direct, db_session
):
    headers = user_headers("user_active@example.com")
    inactive_user = create_user_direct("inactive2@example.com", UserRole.REQUESTER)
    inactive_user.is_active = False
    db_session.commit()
    response = client.get(f"{API_PREFIX}/{inactive_user.id}", headers=headers)
    assert response.status_code == 403


def test_get_users_with_invalid_id(client, user_headers):
    headers = user_headers("user_invalid@example.com")
    response = client.get(f"{API_PREFIX}/abc", headers=headers)
    assert response.status_code == 422


def test_admin_can_get_self_by_id(client, admin_headers):
    headers = admin_headers()
    response = client.get(f"{API_PREFIX}/1", headers=headers)
    assert response.status_code == 200
