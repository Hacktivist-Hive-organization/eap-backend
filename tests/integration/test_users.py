# tests/integration/test_users.py

from app.common.enums import UserRole
from app.common.security import hash_password
from app.core.config import settings
from app.models.db_user import DbUser

API_PREFIX = f"{settings.API_V1_PREFIX}/users"
AUTH_PREFIX = f"{settings.API_V1_PREFIX}/auth"


def register_and_login(client, email: str, role: UserRole = UserRole.REQUESTER):
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


def create_user_direct(db_session, email: str, role: UserRole):
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


def test_get_me(client):
    headers = register_and_login(client, "me@example.com")
    response = client.get(f"{API_PREFIX}/me", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "me@example.com"


def test_get_all_users_as_admin(client, db_session):
    admin = create_user_direct(db_session, "admin@example.com", UserRole.ADMIN)
    user = create_user_direct(db_session, "user@example.com", UserRole.REQUESTER)

    response = client.post(
        f"{AUTH_PREFIX}/login",
        json={"email": "admin@example.com", "password": "StrongP@ss1"},
    )
    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}

    response = client.get(f"{API_PREFIX}/", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) >= 2


def test_get_all_users_as_non_admin(client):
    headers = register_and_login(client, "single@example.com")
    response = client.get(f"{API_PREFIX}/", headers=headers)
    assert response.status_code == 403
    assert len(response.json()) == 1


def test_get_user_by_id_self(client, db_session):
    headers = register_and_login(client, "selfid@example.com")
    user = db_session.query(DbUser).filter_by(email="selfid@example.com").one()
    response = client.get(f"{API_PREFIX}/{user.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["id"] == user.id


def test_get_user_by_id_forbidden(client, db_session):
    headers = register_and_login(client, "user1@example.com")
    other = create_user_direct(db_session, "user2@example.com", UserRole.REQUESTER)
    response = client.get(f"{API_PREFIX}/{other.id}", headers=headers)
    assert response.status_code == 403


def test_update_current_user_profile(client, db_session):
    headers = register_and_login(client, "update@example.com")
    response = client.put(
        f"{API_PREFIX}/me",
        json={"first_name": "New", "last_name": "Name"},
        headers=headers,
    )
    assert response.status_code == 200
    user = db_session.query(DbUser).filter_by(email="update@example.com").one()
    assert user.first_name == "New"
    assert user.last_name == "Name"


def test_update_current_user_profile_validation_error(client):
    headers = register_and_login(client, "invalidupdate@example.com")
    response = client.put(
        f"{API_PREFIX}/me",
        json={"first_name": "", "last_name": "Name"},
        headers=headers,
    )
    assert response.status_code == 422


def test_partial_update_current_user_profile(client, db_session):
    headers = register_and_login(client, "patch@example.com")
    response = client.patch(
        f"{API_PREFIX}/me",
        json={"first_name": "Patched"},
        headers=headers,
    )
    assert response.status_code == 200
    user = db_session.query(DbUser).filter_by(email="patch@example.com").one()
    assert user.first_name == "Patched"
    assert user.last_name == "Doe"


def test_partial_update_current_user_profile_empty_body(client):
    headers = register_and_login(client, "emptypatch@example.com")
    response = client.patch(f"{API_PREFIX}/me", json={}, headers=headers)
    assert response.status_code == 200
