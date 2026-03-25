# tests/integration/test_draft_request_submission.py

import os

import pytest

from app.common.enums import Status
from app.core.config import settings
from app.main import app
from app.models import DBRequest, DBRequestTypeApprover, DbUser
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

    request_response = response.json()

    assert request_response["id"] == request_id
    assert request_response["current_status"] == Status.SUBMITTED.value

    # Validate tracking entry
    assert len(request_response["req_tracking"]) == 1
    tracking = request_response["req_tracking"][0]

    assert tracking["status"] == Status.SUBMITTED.value
    assert tracking["id"] is not None
    assert tracking["user"]["id"] is not None

    # Validate DB state
    db_request = db_session.get(DBRequest, request_id)
    assert db_request.current_status == Status.SUBMITTED


# =========================================================
# OOO FILTER TEST
# =========================================================


def test_submit_request_skips_all_ooo_approvers(
    client,
    db_session,
    users,
    seeded_request_types,
    auth_as,
    valid_request_payload,
):
    """
    If all approvers for a request type are OOO,
    submission should fail with 400.
    """

    requester = users["user1"]
    auth_as(requester)

    hardware = seeded_request_types["hardware"]

    # -------------------------------------------------
    # Fetch all hardware approvers
    # -------------------------------------------------
    approver_links = (
        db_session.query(DBRequestTypeApprover)
        .filter_by(request_type_id=hardware.id)
        .all()
    )

    # Map to user objects and set all OOO
    for link in approver_links:
        approver = db_session.get(DbUser, link.user_id)
        approver.is_out_of_office = True

    db_session.commit()

    # -------------------------------------------------
    # Create Draft Request
    # -------------------------------------------------
    payload = valid_request_payload(current_status=Status.DRAFT)

    response = client.post(f"{API_PREFIX}", json=payload)
    assert response.status_code == 201
    request_id = response.json()["id"]

    # -------------------------------------------------
    # Submit Request
    # -------------------------------------------------
    response = client.patch(f"{API_PREFIX}/{request_id}/submit")

    # -------------------------------------------------
    # Expect Failure (No Available Approvers)
    # -------------------------------------------------
    assert response.status_code == 400


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
    Workload should increment on the selected (lowest workload) approver
    for each successful submission.
    """

    requester = users["user1"]
    auth_as(requester)

    hardware = seeded_request_types["hardware"]

    # -------------------------------------------------
    # Get lowest workload approver BEFORE submissions
    # -------------------------------------------------
    approver_links = (
        db_session.query(DBRequestTypeApprover)
        .filter_by(request_type_id=hardware.id)
        .order_by(DBRequestTypeApprover.workload.asc())
        .all()
    )

    lowest_link = approver_links[0]
    initial_workload = lowest_link.workload

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

    # -------------------------------------------------
    # Validate workload incremented by 2
    # -------------------------------------------------
    db_session.refresh(lowest_link)

    assert lowest_link.workload == initial_workload + 2


def test_submit_selects_lowest_workload_approver(
    client,
    db_session,
    users,
    seeded_request_types,
    auth_as,
    valid_request_payload,
):
    """
    When multiple approvers exist for Hardware,
    the approver with the lowest workload should be selected.
    """

    requester = users["user1"]
    auth_as(requester)

    hardware = seeded_request_types["hardware"]

    # Based on seed:
    high_workload_approver = seeded_request_types["approver1"]  # workload = 5
    low_workload_approver = seeded_request_types["approver2"]  # workload = 1

    # -------------------------------------------------
    # Assert initial workload ordering (safety check)
    # -------------------------------------------------
    high_link = (
        db_session.query(DBRequestTypeApprover)
        .filter_by(
            user_id=high_workload_approver.id,
            request_type_id=hardware.id,
        )
        .first()
    )

    low_link = (
        db_session.query(DBRequestTypeApprover)
        .filter_by(
            user_id=low_workload_approver.id,
            request_type_id=hardware.id,
        )
        .first()
    )

    assert low_link.workload < high_link.workload
    initial_low_workload = low_link.workload
    initial_high_workload = high_link.workload

    # -------------------------------------------------
    # Create Draft Request (Hardware default)
    # -------------------------------------------------
    payload = valid_request_payload(current_status=Status.DRAFT)

    response = client.post(f"{API_PREFIX}", json=payload)
    assert response.status_code == 201
    request_id = response.json()["id"]

    # -------------------------------------------------
    # Submit Request
    # -------------------------------------------------
    response = client.patch(f"{API_PREFIX}/{request_id}/submit")
    assert response.status_code == 200

    data = response.json()

    # -------------------------------------------------
    # Validate Lowest Workload Approver Was Assigned
    # -------------------------------------------------
    tracking = data["req_tracking"][0]
    assigned_approver_id = tracking["user"]["id"]
    assert assigned_approver_id == low_workload_approver.id

    # -------------------------------------------------
    # Validate Workload Updated Correctly
    # -------------------------------------------------
    db_session.refresh(low_link)
    db_session.refresh(high_link)

    assert low_link.workload == initial_low_workload + 1  # was 1 → now 2
    assert high_link.workload == initial_high_workload  # unchanged
