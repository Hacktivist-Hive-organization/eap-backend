import os

import pytest

from app.common.enums import Status
from app.core.config import settings
from app.main import app
from app.models import DBRequest, DBRequestTypeApprover
from app.repositories import RequestTrackingRepository

API_PREFIX = f"{settings.API_V1_PREFIX}/requests"

pytestmark = pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="DbUser.username not ready, skipping temporarily in CI",
)

# =========================================================
# SUCCESS CASE
# =========================================================


def test_submit_request_success(
    client,
    db_session,
    users,
    seeded_request_types,
    auth_as,
    valid_request_payload,
):
    """
    Should:
    - Change status from DRAFT -> SUBMITTED
    - Assign correct approver
    - Increase workload
    - Return tracking version id
    """

    requester = users["user1"]
    auth_as(requester)

    # Create draft request
    payload = valid_request_payload(current_status=Status.DRAFT)

    response = client.post(f"{API_PREFIX}", json=payload)
    assert response.status_code == 201
    request_id = response.json()["id"]

    # Submit draft
    response = client.patch(f"{API_PREFIX}/{request_id}/submit")
    assert response.status_code == 200

    data = response.json()

    assert data["id"] == request_id
    assert data["current_status"] == Status.SUBMITTED.value

    # Validate tracking entry
    assert len(data["req_tracking"]) == 1
    tracking = data["req_tracking"][0]

    assert tracking["status"] == Status.SUBMITTED.value
    assert tracking["id"] is not None
    assert tracking["approver"]["id"] is not None

    # Validate DB state
    db_request = db_session.get(DBRequest, request_id)
    assert db_request.current_status == Status.SUBMITTED

    # Validate workload increment
    approver_link = (
        db_session.query(DBRequestTypeApprover)
        .filter_by(request_type_id=db_request.type_id)
        .first()
    )

    assert approver_link.workload == 1


# =========================================================
# OOO FILTER TEST
# =========================================================


def test_submit_request_skips_ooo_approver(
    client,
    db_session,
    users,
    seeded_request_types,
    auth_as,
    valid_request_payload,
):
    """
    If approver is OOO, request should not be assigned.
    """

    requester = users["user1"]
    auth_as(requester)

    # Set hardware approver OOO
    approver = seeded_request_types["approver1"]
    approver.is_out_of_office = True
    db_session.commit()

    payload = valid_request_payload(current_status=Status.DRAFT)

    response = client.post(f"{API_PREFIX}", json=payload)
    assert response.status_code == 201
    request_id = response.json()["id"]

    response = client.patch(f"{API_PREFIX}/{request_id}/submit")

    # Since hardware only has one approver → expect 400
    assert response.status_code == 400
    assert response.json()["detail"] == "No approver configured for this request type"


# =========================================================
# NOT OWNER TEST
# =========================================================


def test_submit_request_not_owner(
    client,
    users,
    seeded_request_types,
    auth_as,
    valid_request_payload,
):
    """
    Only owner can submit draft.
    """

    owner = users["user1"]
    other_user = users["user2"]

    # Owner creates draft
    auth_as(owner)
    payload = valid_request_payload(current_status=Status.DRAFT)
    response = client.post(f"{API_PREFIX}", json=payload)
    request_id = response.json()["id"]

    # Another user tries to submit
    auth_as(other_user)
    response = client.patch(f"{API_PREFIX}/{request_id}/submit")

    assert response.status_code == 403


# =========================================================
# ALREADY SUBMITTED TEST
# =========================================================


def test_submit_request_already_submitted(
    client,
    users,
    seeded_request_types,
    auth_as,
    valid_request_payload,
):
    requester = users["user1"]
    auth_as(requester)

    # Create draft
    payload = valid_request_payload(current_status=Status.DRAFT)
    response = client.post(f"{API_PREFIX}", json=payload)
    request_id = response.json()["id"]

    # First submission → OK
    response = client.patch(f"{API_PREFIX}/{request_id}/submit")
    assert response.status_code == 200

    # Second submission → Should fail
    response = client.patch(f"{API_PREFIX}/{request_id}/submit")
    assert response.status_code == 400
    assert response.json()["detail"] == "Only draft requests can be submitted"


# =========================================================
# WORKLOAD INCREMENT MULTIPLE SUBMISSIONS
# =========================================================


def test_submit_multiple_requests_increments_workload(
    client,
    db_session,
    users,
    seeded_request_types,
    auth_as,
    valid_request_payload,
):
    """
    Workload should increment per successful submission.
    """

    requester = users["user1"]
    auth_as(requester)

    # -----------------------
    # First request
    # -----------------------
    payload1 = valid_request_payload(current_status=Status.DRAFT)

    response1 = client.post(f"{API_PREFIX}", json=payload1)
    assert response1.status_code == 201
    request_id_1 = response1.json()["id"]

    submit_response_1 = client.patch(f"{API_PREFIX}/{request_id_1}/submit")
    assert submit_response_1.status_code == 200
    assert submit_response_1.json()["current_status"] == Status.SUBMITTED.value

    # -----------------------
    # Second request
    # -----------------------
    payload2 = valid_request_payload(
        title="Second Request",
        current_status=Status.DRAFT,
    )

    response2 = client.post(f"{API_PREFIX}", json=payload2)
    assert response2.status_code == 201
    request_id_2 = response2.json()["id"]

    submit_response_2 = client.patch(f"{API_PREFIX}/{request_id_2}/submit")
    assert submit_response_2.status_code == 200
    assert submit_response_2.json()["current_status"] == Status.SUBMITTED.value

    # -----------------------
    # Validate workload increment
    # -----------------------
    approver_link = (
        db_session.query(DBRequestTypeApprover)
        .filter_by(request_type_id=seeded_request_types["hardware"].id)
        .first()
    )

    assert approver_link.workload == 2
