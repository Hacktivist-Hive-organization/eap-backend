import os

import pytest

from app.common.enums import Priority, Status
from app.core.config import settings
from app.main import app
from app.models import DBRequest, DBRequestTypeApprover, DbUser
from app.repositories import RequestTrackingRepository

API_PREFIX = f"{settings.API_V1_PREFIX}/requests/submit"

pytestmark = pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="DbUser.username not ready, skipping temporarily in CI",
)


def test_create_submitted_request_success(
    client,
    seeded_request_types,
    users,
    auth_as,
    valid_request_payload,
):
    data = seeded_request_types
    owner = users["user1"]
    auth_as(owner)
    payload = valid_request_payload(
        title="new Request",
        current_status=Status.SUBMITTED,
    )

    response = client.post(f"{API_PREFIX}", json=payload)

    assert response.status_code == 201

    body = response.json()

    assert body["current_status"] == Status.SUBMITTED.value
    assert body["type"]["name"] == "Hardware"
    assert body["subtype"]["name"] == "Laptop"
    assert body["updated_at"] is not None


def test_create_request_type_not_found(
    client,
    seeded_request_types,
    users,
    auth_as,
):
    owner = users["user1"]
    auth_as(owner)

    payload = {
        "type_id": 999,
        "subtype_id": 1,
        "title": "Fix printer",
        "description": "Printer broken and cannot print documents.",
        "business_justification": "Office cannot operate without printer.",
        "priority": "low",
        "requester_id": 1,
    }

    response = client.post(f"{API_PREFIX}", json=payload)

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Request type not found: no type exists with id 999"
    }


def test_create_request_subtype_mismatch(client, seeded_request_types, users, auth_as):
    data = seeded_request_types
    owner = users["user1"]
    auth_as(owner)

    payload = {
        "type_id": data["hardware"].id,
        "subtype_id": data["license"].id,  # belongs to software
        "title": "Wrong subtype",
        "description": "Testing wrong subtype validation.",
        "business_justification": "Testing business rules.",
        "priority": "medium",
        "requester_id": users["user1"].id,
    }

    response = client.post(f"{API_PREFIX}", json=payload)

    assert response.status_code == 400
    assert "subtype mismatch" in response.json()["detail"]


def test_create_request_invalid_priority(client, seeded_request_types, users, auth_as):
    data = seeded_request_types
    owner = users["user1"]
    auth_as(owner)

    """Test that invalid priority values are rejected by Pydantic validation"""
    payload = {
        "type_id": data["hardware"].id,
        "subtype_id": data["laptop"].id,
        "title": "Fix laptop",
        "description": "Laptop does not start properly and needs repair.",
        "business_justification": "Employee cannot work without laptop.",
        "priority": "URGENT",  # Invalid
    }

    response = client.post(f"{API_PREFIX}", json=payload)

    assert response.status_code == 422
    assert (
        "priority: Input should be 'low', 'medium' or 'high'"
        in response.json()["detail"]
    )


def test_create_request_status_defaults_to_submitted(
    client, seeded_request_types, users, auth_as
):
    data = seeded_request_types
    owner = users["user1"]
    auth_as(owner)

    """Test that status is defaulted to Submitted if not provided"""
    payload = {
        "type_id": data["hardware"].id,
        "subtype_id": data["laptop"].id,
        "title": "Install Zoom",
        "description": "Need Zoom installed on new laptop for remote meetings.",
        "business_justification": "Required for remote collaboration.",
        "priority": "medium",
        "requester_id": users["user1"].id,
    }

    response = client.post(f"{API_PREFIX}", json=payload)
    body = response.json()

    assert response.status_code == 201
    assert body["current_status"] == Status.SUBMITTED
    assert body["priority"] == Priority.MEDIUM


def test_create_request_status_always_submitted(
    client, seeded_request_types, users, auth_as
):
    data = seeded_request_types
    owner = users["user1"]
    auth_as(owner)

    """Test that status is always submitted on create, even if FE sends 
    another value"""
    payload = {
        "type_id": data["hardware"].id,
        "subtype_id": data["laptop"].id,
        "title": "Install Zoom",
        "description": "Need Zoom installed on new laptop for remote meetings.",
        "business_justification": "Required for remote collaboration.",
        "priority": "high",
        "current_status": "draft",  # FE tries to override
        "requester_id": users["user1"].id,
    }

    response = client.post(f"{API_PREFIX}", json=payload)
    body = response.json()

    assert response.status_code == 201
    # Status is always Draft
    assert body["current_status"] == Status.SUBMITTED
    # Priority is accepted correctly
    assert body["priority"] == Priority.HIGH


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
    data = seeded_request_types
    hardware = data["hardware"]

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

    payload = {
        "type_id": data["hardware"].id,
        "subtype_id": data["laptop"].id,
        "title": "Fix laptop",
        "description": "Laptop does not start properly and needs repair.",
        "business_justification": "Employee cannot work without laptop.",
        "priority": "high",
    }

    response = client.post(f"{API_PREFIX}", json=payload)

    # -------------------------------------------------
    # Expect Failure (No Available Approvers)
    # -------------------------------------------------
    assert response.status_code == 400
    assert response.json()["detail"] == "No approver configured for this request type"


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
    payload1 = valid_request_payload(current_status=Status.SUBMITTED)

    response1 = client.post(f"{API_PREFIX}", json=payload1)
    assert response1.status_code == 201
    assert response1.json()["current_status"] == Status.SUBMITTED.value

    # -----------------------
    # Second request
    # -----------------------
    payload2 = valid_request_payload(
        title="Second Request",
        current_status=Status.SUBMITTED,
    )

    response2 = client.post(f"{API_PREFIX}", json=payload2)
    assert response2.status_code == 201

    assert response2.json()["current_status"] == Status.SUBMITTED.value

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
    data = seeded_request_types
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

    payload = valid_request_payload(
        title="new Request",
        current_status=Status.SUBMITTED,
    )

    response = client.post(f"{API_PREFIX}", json=payload)
    assert response.status_code == 201
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
