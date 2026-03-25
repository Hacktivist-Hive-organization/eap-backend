# tests/integration/test_edit_draft_request.py

import os

import pytest

from app.common.enums import Status
from app.core.config import settings
from app.models import DBRequest

API_PREFIX = f"{settings.API_V1_PREFIX}/requests"

pytestmark = pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="Skipping temporarily in CI",
)

# =========================================================
# SUCCESS CASE
# =========================================================


def test_edit_draft_request_success(
    client,
    db_session,
    users,
    auth_as,
    valid_request_payload,
):
    """
    Should allow requester to edit their draft request
    """

    user = users["user1"]
    auth_as(user)

    # Create draft
    payload = valid_request_payload(current_status=Status.DRAFT)
    response = client.post(f"{API_PREFIX}", json=payload)
    assert response.status_code == 201
    request_id = response.json()["id"]

    #  Edit only title
    update_payload = {"title": "Updated Title"}

    response = client.patch(f"{API_PREFIX}/{request_id}/edit", json=update_payload)

    # assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"

    # Validate DB
    db_request = db_session.get(DBRequest, request_id)
    assert db_request.title == "Updated Title"


# =========================================================
# NOT OWNER
# =========================================================


def test_edit_draft_request_not_owner(
    client,
    users,
    auth_as,
    valid_request_payload,
):
    owner = users["user1"]
    other_user = users["user2"]

    # Owner creates draft
    auth_as(owner)
    payload = valid_request_payload(current_status=Status.DRAFT)
    response = client.post(f"{API_PREFIX}", json=payload)
    request_id = response.json()["id"]

    # Other user tries to edit
    auth_as(other_user)

    response = client.patch(
        f"{API_PREFIX}/{request_id}/edit",
        json={"title": "Hacked"},
    )

    assert response.status_code == 403


# =========================================================
# NOT DRAFT
# =========================================================

#
# def test_edit_request_not_draft(
#     client,
#     users,
#     auth_as,
#     valid_request_payload,
# ):
#     user = users["user1"]
#     auth_as(user)
#
#     # Create and submit
#     payload = valid_request_payload(current_status=Status.DRAFT)
#     response = client.post(f"{API_PREFIX}", json=payload)
#     request_id = response.json()["id"]
#
#     client.patch(f"{API_PREFIX}/{request_id}/submit")
#
#     # Try editing after submission
#     response = client.patch(
#         f"{API_PREFIX}/{request_id}/edit",
#         json={"title": "Should fail"},
#     )
#
#     assert response.status_code == 400
#     assert response.json()["detail"] == "Only draft requests can be edited"


# =========================================================
# FORBIDDEN FIELD (STATUS)
# =========================================================


def test_edit_request_partial_update_ignores_status(
    client,
    users,
    auth_as,
    valid_request_payload,
):
    """
    Frontend may send `current_status` along with allowed fields.
    Endpoint should ignore `current_status` and update only allowed fields.
    """

    user = users["user1"]
    auth_as(user)

    # Create a draft request
    payload = valid_request_payload(current_status=Status.DRAFT)
    response = client.post(f"{API_PREFIX}", json=payload)
    assert response.status_code == 201
    request_id = response.json()["id"]

    # Attempt to update title AND send forbidden current_status
    update_payload = {
        "title": "Updated Title",
        "current_status": Status.APPROVED.value,  # frontend may send this
    }
    response = client.patch(
        f"{API_PREFIX}/{request_id}/edit",
        json=update_payload,
    )
    assert response.status_code == 200
    data = response.json()

    # Validate title updated
    assert data["title"] == "Updated Title"

    # Validate status remains DRAFT
    assert data["current_status"] == Status.DRAFT.value


# =========================================================
# INVALID DATA (VALIDATION)
# =========================================================


def test_edit_request_invalid_data(
    client,
    users,
    auth_as,
    valid_request_payload,
):
    user = users["user1"]
    auth_as(user)

    payload = valid_request_payload(current_status=Status.DRAFT)
    response = client.post(f"{API_PREFIX}", json=payload)
    request_id = response.json()["id"]

    # Invalid title (too short)
    response = client.patch(
        f"{API_PREFIX}/{request_id}/edit",
        json={"title": "abc"},
    )

    assert response.status_code == 422


# =========================================================
# REQUEST NOT FOUND
# =========================================================


def test_edit_request_not_found(
    client,
    users,
    auth_as,
):
    user = users["user1"]
    auth_as(user)

    response = client.patch(
        f"{API_PREFIX}/999999/edit",
        json={"title": "Doesn't exist"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Request not found"
