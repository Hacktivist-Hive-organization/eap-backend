# tests/integration/users/test_users_self_update.py

from app.core.config import settings
from app.models.db_user import DbUser

API_PREFIX = f"{settings.API_V1_PREFIX}/users"
AUTH_PREFIX = f"{settings.API_V1_PREFIX}/auth"


def register_and_login(client, email: str):
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


def get_user(db_session, email: str):
    return db_session.query(DbUser).filter_by(email=email).one()


def test_update_first_and_last_name(client, db_session):
    headers = register_and_login(client, "selfupdate1@example.com")
    response = client.patch(
        f"{API_PREFIX}/me",
        json={"first_name": "New", "last_name": "Name"},
        headers=headers,
    )
    assert response.status_code == 200
    user = get_user(db_session, "selfupdate1@example.com")
    assert user.first_name == "New"
    assert user.last_name == "Name"


def test_update_only_first_name(client, db_session):
    headers = register_and_login(client, "selfupdate2@example.com")
    response = client.patch(
        f"{API_PREFIX}/me",
        json={"first_name": "Changed"},
        headers=headers,
    )
    assert response.status_code == 200
    user = get_user(db_session, "selfupdate2@example.com")
    assert user.first_name == "Changed"
    assert user.last_name == "Doe"


def test_update_only_last_name(client, db_session):
    headers = register_and_login(client, "selfupdate3@example.com")
    response = client.patch(
        f"{API_PREFIX}/me",
        json={"last_name": "Changed"},
        headers=headers,
    )
    assert response.status_code == 200
    user = get_user(db_session, "selfupdate3@example.com")
    assert user.first_name == "John"
    assert user.last_name == "Changed"


def test_update_out_of_office_flag(client, db_session):
    headers = register_and_login(client, "selfupdate4@example.com")
    response = client.patch(
        f"{API_PREFIX}/me",
        json={"is_out_of_office": True},
        headers=headers,
    )
    assert response.status_code == 200
    user = get_user(db_session, "selfupdate4@example.com")
    assert user.is_out_of_office is True


def test_update_multiple_fields(client, db_session):
    headers = register_and_login(client, "selfupdate5@example.com")
    response = client.patch(
        f"{API_PREFIX}/me",
        json={
            "first_name": "Updated",
            "last_name": "User",
            "is_out_of_office": True,
        },
        headers=headers,
    )
    assert response.status_code == 200
    user = get_user(db_session, "selfupdate5@example.com")
    assert user.first_name == "Updated"
    assert user.last_name == "User"
    assert user.is_out_of_office is True


def test_update_with_empty_body(client, db_session):
    headers = register_and_login(client, "selfupdate6@example.com")
    response = client.patch(f"{API_PREFIX}/me", json={}, headers=headers)
    assert response.status_code == 200
    user = get_user(db_session, "selfupdate6@example.com")
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.is_out_of_office is False


def test_update_with_empty_first_name_validation_error(client):
    headers = register_and_login(client, "selfupdate7@example.com")
    response = client.patch(
        f"{API_PREFIX}/me",
        json={"first_name": ""},
        headers=headers,
    )
    assert response.status_code == 422


def test_update_with_empty_last_name_validation_error(client):
    headers = register_and_login(client, "selfupdate8@example.com")
    response = client.patch(
        f"{API_PREFIX}/me",
        json={"last_name": ""},
        headers=headers,
    )
    assert response.status_code == 422


def test_update_with_whitespace_names_stripped(client, db_session):
    headers = register_and_login(client, "selfupdate9@example.com")
    response = client.patch(
        f"{API_PREFIX}/me",
        json={"first_name": "  Alice  ", "last_name": "  Smith  "},
        headers=headers,
    )
    assert response.status_code == 200
    user = get_user(db_session, "selfupdate9@example.com")
    assert user.first_name == "Alice"
    assert user.last_name == "Smith"


def test_update_with_whitespace_only_names_validation_error(client):
    headers = register_and_login(client, "selfupdate10@example.com")
    response = client.patch(
        f"{API_PREFIX}/me",
        json={"first_name": "   ", "last_name": "   "},
        headers=headers,
    )
    assert response.status_code == 422


def test_update_ignores_unknown_fields(client, db_session):
    headers = register_and_login(client, "selfupdate11@example.com")
    user = get_user(db_session, "selfupdate11@example.com")
    original_role = user.role
    original_active = user.is_active

    response = client.patch(
        f"{API_PREFIX}/me",
        json={
            "first_name": "Valid",
            "role": "admin",
            "is_active": False,
            "unknown_field": "ignored",
        },
        headers=headers,
    )
    assert response.status_code == 200
    db_session.expire_all()
    user = get_user(db_session, "selfupdate11@example.com")
    assert user.first_name == "Valid"
    assert user.role == original_role
    assert user.is_active == original_active


def test_multiple_consecutive_updates(client, db_session):
    headers = register_and_login(client, "selfupdate12@example.com")
    response = client.patch(
        f"{API_PREFIX}/me", json={"first_name": "Step1"}, headers=headers
    )
    assert response.status_code == 200
    user = get_user(db_session, "selfupdate12@example.com")
    assert user.first_name == "Step1"

    response = client.patch(
        f"{API_PREFIX}/me", json={"last_name": "Step2"}, headers=headers
    )
    assert response.status_code == 200
    user = get_user(db_session, "selfupdate12@example.com")
    assert user.last_name == "Step2"


def test_update_out_of_office_toggle(client, db_session):
    headers = register_and_login(client, "selfupdate13@example.com")
    response = client.patch(
        f"{API_PREFIX}/me", json={"is_out_of_office": True}, headers=headers
    )
    assert response.status_code == 200
    user = get_user(db_session, "selfupdate13@example.com")
    assert user.is_out_of_office is True

    response = client.patch(
        f"{API_PREFIX}/me", json={"is_out_of_office": False}, headers=headers
    )
    assert response.status_code == 200
    user = get_user(db_session, "selfupdate13@example.com")
    assert user.is_out_of_office is False


def test_update_with_unicode_names(client, db_session):
    headers = register_and_login(client, "selfupdate14@example.com")
    response = client.patch(
        f"{API_PREFIX}/me",
        json={"first_name": "Иван", "last_name": "李"},
        headers=headers,
    )
    assert response.status_code == 200
    user = get_user(db_session, "selfupdate14@example.com")
    assert user.first_name == "Иван"
    assert user.last_name == "李"


def test_update_long_strings(client, db_session):
    headers = register_and_login(client, "selfupdate15@example.com")
    long_name = "A" * 255
    response = client.patch(
        f"{API_PREFIX}/me",
        json={"first_name": long_name, "last_name": long_name},
        headers=headers,
    )
    assert response.status_code == 200
    user = get_user(db_session, "selfupdate15@example.com")
    assert user.first_name == long_name
    assert user.last_name == long_name


def test_update_first_name_with_number_type_validation_error(client):
    headers = register_and_login(client, "selfupdate16@example.com")
    response = client.patch(
        f"{API_PREFIX}/me",
        json={"first_name": 123},
        headers=headers,
    )
    assert response.status_code == 422


def test_update_last_name_with_number_type_validation_error(client):
    headers = register_and_login(client, "selfupdate17@example.com")
    response = client.patch(
        f"{API_PREFIX}/me",
        json={"last_name": 456},
        headers=headers,
    )
    assert response.status_code == 422


def test_update_is_out_of_office_with_string_type_validation_error(client):
    headers = register_and_login(client, "selfupdate18@example.com")
    response = client.patch(
        f"{API_PREFIX}/me",
        json={"is_out_of_office": "true"},
        headers=headers,
    )
    assert response.status_code == 422


def test_update_first_name_with_min_length_boundary(client, db_session):
    headers = register_and_login(client, "selfupdate19@example.com")
    response = client.patch(
        f"{API_PREFIX}/me",
        json={"first_name": "A"},
        headers=headers,
    )
    assert response.status_code == 200
    user = get_user(db_session, "selfupdate19@example.com")
    assert user.first_name == "A"


def test_update_last_name_exceeding_max_length(client):
    headers = register_and_login(client, "selfupdate20@example.com")
    too_long = "B" * 256
    response = client.patch(
        f"{API_PREFIX}/me",
        json={"last_name": too_long},
        headers=headers,
    )
    assert response.status_code == 422
