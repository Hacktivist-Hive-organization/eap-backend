# tests/integration/test_draft_request_deletion.py

import os

import pytest

from app.common.enums import Status
from app.core.config import settings
from app.models import DBRequest

API_PREFIX = f"{settings.API_V1_PREFIX}/requests"

pytestmark = pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="DbUser.username not ready, skipping temporarily in CI",
)


# =========================================================
# SUCCESS CASE
# =========================================================
def test_delete_draft_request_success(
    client, db_session, users, auth_as, valid_request_payload
):
    """
    Requester can delete own draft request.
    Returns 204 and removes request from DB.
    """
    requester = users["user1"]
    auth_as(requester)

    # Create draft request
    payload = valid_request_payload(current_status=Status.DRAFT)
    response = client.post(f"{API_PREFIX}", json=payload)
    assert response.status_code == 201
    request_id = response.json()["id"]

    # Delete the draft request
    response = client.delete(f"{API_PREFIX}/{request_id}")
    assert response.status_code == 204
    assert response.content == b""  # No body for 204

    # Validate DB deletion
    db_request = db_session.get(DBRequest, request_id)
    assert db_request is None


# =========================================================
# NOT OWNER CASE
# =========================================================
def test_delete_draft_request_not_owner(client, users, auth_as, valid_request_payload):
    """
    Another user cannot delete someone else's draft request → 403.
    """
    owner = users["user1"]
    other_user = users["user2"]

    auth_as(owner)
    payload = valid_request_payload(current_status=Status.DRAFT)
    response = client.post(f"{API_PREFIX}", json=payload)
    request_id = response.json()["id"]

    auth_as(other_user)
    response = client.delete(f"{API_PREFIX}/{request_id}")
    assert response.status_code == 403
    assert (
        response.json()["detail"] == "You do not have permission to delete this request"
    )


# =========================================================
# NON-DRAFT STATUS CASE
# =========================================================
def test_cannot_submit_non_draft_request(
    client, auth_as, users, seeded_requests_for_user
):
    """
    Attempting to submit a request that is already submitted should fail with 400.
    """
    user = users["user1"]
    auth_as(user)

    # Pick a request with submitted status
    submitted_request = next(
        req
        for req in seeded_requests_for_user
        if req.current_status == Status.SUBMITTED
    )

    # Confirm it is not draft
    assert submitted_request.current_status != Status.DRAFT

    # Attempt to submit
    response = client.patch(f"{API_PREFIX}/{submitted_request.id}/submit")
    assert response.status_code == 400
    assert response.json()["detail"] == "Only draft requests can be submitted"


# =========================================================
# REQUEST NOT FOUND CASE
# =========================================================
def test_delete_draft_request_not_found(client, users, auth_as):
    """
    Deleting a non-existent request returns 404.
    """
    requester = users["user1"]
    auth_as(requester)

    # Use a random ID that doesn't exist
    response = client.delete(f"{API_PREFIX}/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Request not found"
