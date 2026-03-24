# tests/integration/users/test_users_admin_update.py

import pytest

from app.common.enums import UserRole
from app.common.security import hash_password
from app.core.config import settings
from app.models.db_user import DbUser

API_PREFIX = f"{settings.API_V1_PREFIX}/users"
AUTH_PREFIX = f"{settings.API_V1_PREFIX}/auth"


@pytest.fixture
def create_users(db_session):
    admin = DbUser(
        email="admin@example.com",
        first_name="System",
        last_name="Admin",
        hashed_password=hash_password("Password123!"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    user = DbUser(
        email="user@example.com",
        first_name="John",
        last_name="Doe",
        hashed_password=hash_password("Password123!"),
        role=UserRole.REQUESTER,
        is_active=True,
    )
    db_session.add_all([admin, user])
    db_session.commit()
    return admin, user


def login_user(client, email: str, password="Password123!"):
    response = client.post(
        f"{AUTH_PREFIX}/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_admin_can_update_first_name_only(client, db_session, create_users):
    admin, user = create_users
    headers = login_user(client, "admin@example.com")

    response = client.patch(
        f"{API_PREFIX}/{user.id}",
        json={"first_name": "Alice"},
        headers=headers,
    )

    assert response.status_code == 200
    user_db = db_session.get(DbUser, user.id)
    assert user_db.first_name == "Alice"
    assert user_db.last_name == "Doe"


def test_admin_can_update_last_name_only(client, db_session, create_users):
    admin, user = create_users
    headers = login_user(client, "admin@example.com")

    response = client.patch(
        f"{API_PREFIX}/{user.id}",
        json={"last_name": "Smith"},
        headers=headers,
    )

    assert response.status_code == 200
    user_db = db_session.get(DbUser, user.id)
    assert user_db.first_name == "John"
    assert user_db.last_name == "Smith"


def test_admin_can_toggle_is_out_of_office(client, db_session, create_users):
    admin, user = create_users
    headers = login_user(client, "admin@example.com")

    response = client.patch(
        f"{API_PREFIX}/{user.id}",
        json={"is_out_of_office": True},
        headers=headers,
    )

    assert response.status_code == 200
    user_db = db_session.get(DbUser, user.id)
    assert user_db.is_out_of_office is True

    response = client.patch(
        f"{API_PREFIX}/{user.id}",
        json={"is_out_of_office": False},
        headers=headers,
    )

    assert response.status_code == 200
    user_db = db_session.get(DbUser, user.id)
    assert user_db.is_out_of_office is False


def test_admin_can_update_role_and_is_active(client, db_session, create_users):
    admin, user = create_users
    headers = login_user(client, "admin@example.com")

    response = client.patch(
        f"{API_PREFIX}/{user.id}",
        json={"role": "approver", "is_active": False},
        headers=headers,
    )

    assert response.status_code == 200
    user_db = db_session.get(DbUser, user.id)
    assert user_db.role == "approver"
    assert user_db.is_active is False


def test_admin_can_update_multiple_fields(client, db_session, create_users):
    admin, user = create_users
    headers = login_user(client, "admin@example.com")

    payload = {
        "first_name": "Alice",
        "last_name": "Smith",
        "is_out_of_office": True,
        "role": "approver",
        "is_active": False,
    }

    response = client.patch(f"{API_PREFIX}/{user.id}", json=payload, headers=headers)

    assert response.status_code == 200
    user_db = db_session.get(DbUser, user.id)
    assert user_db.first_name == "Alice"
    assert user_db.last_name == "Smith"
    assert user_db.is_out_of_office is True
    assert user_db.role == "approver"
    assert user_db.is_active is False


def test_admin_update_ignores_unknown_fields(client, db_session, create_users):
    admin, user = create_users
    headers = login_user(client, "admin@example.com")

    payload = {"first_name": "Valid", "unknown_field": "ignored"}

    response = client.patch(f"{API_PREFIX}/{user.id}", json=payload, headers=headers)

    assert response.status_code == 200
    user_db = db_session.get(DbUser, user.id)
    assert user_db.first_name == "Valid"
    assert not hasattr(user_db, "unknown_field")


def test_admin_update_empty_strings_validation_error(client, db_session, create_users):
    admin, user = create_users
    headers = login_user(client, "admin@example.com")

    response = client.patch(
        f"{API_PREFIX}/{user.id}", json={"first_name": ""}, headers=headers
    )
    assert response.status_code == 422

    response = client.patch(
        f"{API_PREFIX}/{user.id}", json={"last_name": ""}, headers=headers
    )
    assert response.status_code == 422


def test_admin_update_whitespace_strings_validation_error(
    client, db_session, create_users
):
    admin, user = create_users
    headers = login_user(client, "admin@example.com")

    response = client.patch(
        f"{API_PREFIX}/{user.id}",
        json={"first_name": "   ", "last_name": "   "},
        headers=headers,
    )

    assert response.status_code == 422


def test_admin_update_trims_first_name(client, db_session, create_users):
    admin, user = create_users
    headers = login_user(client, "admin@example.com")

    response = client.patch(
        f"{API_PREFIX}/{user.id}",
        json={"first_name": "  Alice  "},
        headers=headers,
    )

    assert response.status_code == 200
    user_db = db_session.get(DbUser, user.id)
    assert user_db.first_name == "Alice"


def test_admin_update_trims_last_name(client, db_session, create_users):
    admin, user = create_users
    headers = login_user(client, "admin@example.com")

    response = client.patch(
        f"{API_PREFIX}/{user.id}",
        json={"last_name": "  Smith  "},
        headers=headers,
    )

    assert response.status_code == 200
    user_db = db_session.get(DbUser, user.id)
    assert user_db.last_name == "Smith"


def test_admin_update_user_not_found(client, create_users):
    admin, _ = create_users
    headers = login_user(client, "admin@example.com")

    response = client.patch(
        f"{API_PREFIX}/999999",
        json={"first_name": "Alice"},
        headers=headers,
    )

    assert response.status_code == 404


def test_admin_update_email_field_ignored(client, db_session, create_users):
    admin, user = create_users
    headers = login_user(client, "admin@example.com")

    response = client.patch(
        f"{API_PREFIX}/{user.id}",
        json={"email": "new@email.com"},
        headers=headers,
    )

    assert response.status_code == 200
    user_db = db_session.get(DbUser, user.id)
    assert user_db.email == "user@example.com"


def test_admin_can_update_is_active_only(client, db_session, create_users):
    admin, user = create_users
    headers = login_user(client, "admin@example.com")

    response = client.patch(
        f"{API_PREFIX}/{user.id}",
        json={"is_active": False},
        headers=headers,
    )

    assert response.status_code == 200
    user_db = db_session.get(DbUser, user.id)
    assert user_db.is_active is False


def test_admin_can_update_role_only(client, db_session, create_users):
    admin, user = create_users
    headers = login_user(client, "admin@example.com")

    response = client.patch(
        f"{API_PREFIX}/{user.id}",
        json={"role": "approver"},
        headers=headers,
    )

    assert response.status_code == 200
    user_db = db_session.get(DbUser, user.id)
    assert user_db.role == "approver"


def test_admin_update_first_name_none_validation_error(client, create_users):
    admin, user = create_users
    headers = login_user(client, "admin@example.com")

    response = client.patch(
        f"{API_PREFIX}/{user.id}",
        json={"first_name": None},
        headers=headers,
    )

    assert response.status_code == 422


def test_admin_update_last_name_none_validation_error(client, create_users):
    admin, user = create_users
    headers = login_user(client, "admin@example.com")

    response = client.patch(
        f"{API_PREFIX}/{user.id}",
        json={"last_name": None},
        headers=headers,
    )

    assert response.status_code == 422


def test_non_admin_cannot_update_user(client, db_session, create_users):
    admin, user = create_users

    non_admin = DbUser(
        email="user_nonadmin@example.com",
        first_name="Not",
        last_name="Admin",
        hashed_password=hash_password("Password123!"),
        role=UserRole.REQUESTER,
        is_active=True,
    )

    db_session.add(non_admin)
    db_session.commit()

    headers = login_user(client, "user_nonadmin@example.com")

    response = client.patch(
        f"{API_PREFIX}/{user.id}",
        json={"first_name": "Alice"},
        headers=headers,
    )

    assert response.status_code == 403


def test_admin_update_id_ignored(client, db_session, create_users):
    admin, user = create_users
    headers = login_user(client, "admin@example.com")

    response = client.patch(
        f"{API_PREFIX}/{user.id}",
        json={"id": 999},
        headers=headers,
    )

    assert response.status_code == 200

    user_db = db_session.get(DbUser, user.id)
    assert user_db.id == user.id


def test_admin_update_empty_payload(client, db_session, create_users):
    admin, user = create_users
    headers = login_user(client, "admin@example.com")

    response = client.patch(
        f"{API_PREFIX}/{user.id}",
        json={},
        headers=headers,
    )

    assert response.status_code == 200

    user_db = db_session.get(DbUser, user.id)

    assert user_db.first_name == "John"
    assert user_db.last_name == "Doe"
    assert user_db.role == UserRole.REQUESTER
    assert user_db.is_active is True
    assert user_db.is_out_of_office is False


def test_admin_update_first_name_exceeding_max_length(client, db_session, create_users):
    admin, user = create_users
    headers = login_user(client, "admin@example.com")
    too_long = "A" * 256
    response = client.patch(
        f"{API_PREFIX}/{user.id}",
        json={"first_name": too_long},
        headers=headers,
    )
    assert response.status_code == 422


def test_admin_update_last_name_exceeding_max_length(client, db_session, create_users):
    admin, user = create_users
    headers = login_user(client, "admin@example.com")
    too_long = "B" * 256
    response = client.patch(
        f"{API_PREFIX}/{user.id}",
        json={"last_name": too_long},
        headers=headers,
    )
    assert response.status_code == 422


def test_admin_update_is_out_of_office_with_string_type_validation_error(
    client, db_session, create_users
):
    admin, user = create_users
    headers = login_user(client, "admin@example.com")
    response = client.patch(
        f"{API_PREFIX}/{user.id}",
        json={"is_out_of_office": "true"},
        headers=headers,
    )
    assert response.status_code == 422


def test_admin_update_unicode_names(client, db_session, create_users):
    admin, user = create_users
    headers = login_user(client, "admin@example.com")
    payload = {"first_name": "Иван", "last_name": "李"}
    response = client.patch(f"{API_PREFIX}/{user.id}", json=payload, headers=headers)
    assert response.status_code == 200
    user_db = db_session.get(DbUser, user.id)
    assert user_db.first_name == "Иван"
    assert user_db.last_name == "李"


def test_admin_update_max_length_names(client, db_session, create_users):
    admin, user = create_users
    headers = login_user(client, "admin@example.com")
    max_length_name = "X" * 255
    payload = {"first_name": max_length_name, "last_name": max_length_name}
    response = client.patch(f"{API_PREFIX}/{user.id}", json=payload, headers=headers)
    assert response.status_code == 200
    user_db = db_session.get(DbUser, user.id)
    assert user_db.first_name == max_length_name
    assert user_db.last_name == max_length_name


def test_admin_cannot_downgrade_own_admin_role(client, db_session, create_users):
    admin, _ = create_users
    headers = login_user(client, "admin@example.com")
    response = client.patch(
        f"{API_PREFIX}/{admin.id}",
        json={"role": "requester"},
        headers=headers,
    )
    assert response.status_code == 403
