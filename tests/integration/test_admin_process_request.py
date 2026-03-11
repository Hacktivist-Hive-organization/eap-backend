# tests/integration/test_admin_process_request.py

import os

import pytest

from app.common.enums import Status
from app.core.config import settings
from app.models import DBRequestTracking

API_PREFIX = f"{settings.API_V1_PREFIX}/admin/requests"

pytestmark = pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="DbUser.username not ready, skipping temporarily in CI",
)


# -------------------------------------------------
# Fixture: assign requests with tracking
# -------------------------------------------------
@pytest.fixture
def requests_with_tracking(db_session, users, seeded_requests_for_user):
    """
    Seed requests with initial tracking entries:
    - 1 SUBMITTED
    - 2 APPROVED
    - 1 REJECTED
    """
    approver = users["user2"]  # arbitrary approver

    # Assign deterministic statuses
    seeded_requests_for_user[0].current_status = Status.SUBMITTED
    seeded_requests_for_user[1].current_status = Status.APPROVED
    seeded_requests_for_user[2].current_status = Status.APPROVED
    seeded_requests_for_user[3].current_status = Status.APPROVED
    seeded_requests_for_user[4].current_status = Status.REJECTED

    db_session.flush()

    # Add tracking
    for req in seeded_requests_for_user:
        db_session.add(
            DBRequestTracking(
                request_id=req.id,
                user_id=approver.id,
                status=req.current_status,
                comment="Initial tracking for tests",
            )
        )

    db_session.commit()

    return {
        "approver": approver,
        "requests": seeded_requests_for_user,
    }


# -------------------------------------------------
# SUCCESS TESTS
# -------------------------------------------------
def test_admin_process_request_assign_success(
    client,
    dashboard_admin,
    requests_with_tracking,
    auth_as,
):
    """
    Admin assigns an APPROVED request to self (IN_PROGRESS).
    """
    admin = dashboard_admin["admin1"]
    requests = requests_with_tracking["requests"]
    request = requests[1]  # APPROVED

    # Ensure no admin assigned yet
    request.assignee.id = requests_with_tracking["approver"].id

    auth_as(admin)

    response = client.patch(
        f"{API_PREFIX}/{request.id}",
        params={"status": Status.IN_PROGRESS.value, "comment": "Start work"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["current_status"] == Status.IN_PROGRESS.value
    assert data["assignee"]["id"] == admin.id


def test_admin_process_request_complete_success(
    client,
    dashboard_admin,
    requests_with_tracking,
    auth_as,
):
    """
    Admin completes an IN_PROGRESS request.
    """
    admin = dashboard_admin["admin1"]
    requests = requests_with_tracking["requests"]
    request = requests[2]  # APPROVED initially
    request.current_status = Status.IN_PROGRESS

    auth_as(admin)

    response = client.patch(
        f"{API_PREFIX}/{request.id}",
        params={"status": Status.COMPLETED.value, "comment": "Done work"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["current_status"] == Status.COMPLETED.value
    assert data["assignee"]["id"] == admin.id


def test_admin_process_request_reject_success(
    client,
    dashboard_admin,
    requests_with_tracking,
    auth_as,
):
    """
    Admin rejects an IN_PROGRESS request (requires comment).
    """
    admin = dashboard_admin["admin1"]
    requests = requests_with_tracking["requests"]
    request = requests[3]  # APPROVED initially
    request.current_status = Status.IN_PROGRESS

    auth_as(admin)

    response = client.patch(
        f"{API_PREFIX}/{request.id}",
        params={"status": Status.REJECTED.value, "comment": "Invalid request"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["current_status"] == Status.REJECTED.value
    assert data["assignee"]["id"] == admin.id


# -------------------------------------------------
# FAILURE TESTS
# -------------------------------------------------
def test_admin_cannot_assign_if_another_admin_assigned(
    client,
    dashboard_admin,
    requests_with_tracking,
    auth_as,
):
    """
    Another admin is already assigned → should fail.
    """
    admin1 = dashboard_admin["admin1"]
    admin2 = dashboard_admin["admin2"]
    requests = requests_with_tracking["requests"]
    request = requests[2]  # APPROVED

    auth_as(admin1)
    response = client.patch(
        f"{API_PREFIX}/{request.id}",
        params={"status": Status.IN_PROGRESS.value},
    )
    # admin1 assigned already
    assert response.status_code == 200
    data = response.json()
    assert data["current_status"] == Status.IN_PROGRESS.value
    assert data["assignee"]["id"] == admin1.id

    # Try to assign
    auth_as(admin2)

    response = client.patch(
        f"{API_PREFIX}/{request.id}",
        params={"status": Status.IN_PROGRESS.value},
    )

    assert response.status_code == 400
    assert "Another admin already working" in response.json()["detail"]


def test_admin_cannot_reject_without_comment(
    client,
    dashboard_admin,
    requests_with_tracking,
    auth_as,
):
    """
    Rejecting requires comment.
    """
    admin = dashboard_admin["admin1"]
    requests = requests_with_tracking["requests"]
    request = requests[2]
    request.current_status = Status.IN_PROGRESS

    auth_as(admin)

    response = client.patch(
        f"{API_PREFIX}/{request.id}",
        params={"status": Status.REJECTED.value},
    )

    assert response.status_code == 400
    assert "Comment is mandatory for rejection" in response.json()["detail"]


def test_non_admin_cannot_process_request(
    client,
    users,
    requests_with_tracking,
    auth_as,
):
    """
    Only admins can process requests.
    """
    user = users["user1"]
    requests = requests_with_tracking["requests"]
    request = requests[1]
    request.current_status = Status.APPROVED

    auth_as(user)

    response = client.patch(
        f"{API_PREFIX}/{request.id}",
        params={"status": Status.IN_PROGRESS.value, "comment": "Start work"},
    )

    assert response.status_code == 403
    assert "permission" in response.json()["detail"].lower()


def test_cannot_process_approvers_statuses(
    client,
    dashboard_admin,
    requests_with_tracking,
    auth_as,
):
    """
    Only IN_PROGRESS, COMPLETED, REJECTED allowed.
    """
    admin = dashboard_admin["admin1"]
    requests = requests_with_tracking["requests"]
    request = requests[1]
    request.current_status = Status.APPROVED

    auth_as(admin)

    response = client.patch(
        f"{API_PREFIX}/{request.id}",
        params={"status": Status.APPROVED.value, "comment": "Try to approve"},
    )

    assert response.status_code == 400
    assert (
        "invalid status transition, status should be in_progress, "
        "completed or rejected"
    ) in response.json()["detail"].lower()


def test_admin_cannot_approve_requester(
    client,
    dashboard_admin,
    requests_with_tracking,
    auth_as,
):
    """
    Only IN_PROGRESS, COMPLETED, REJECTED allowed.
    """
    admin = dashboard_admin["admin1"]
    requests = requests_with_tracking["requests"]
    request = requests[1]
    request.current_status = Status.APPROVED

    auth_as(admin)

    response = client.patch(
        f"{API_PREFIX}/{request.id}",
        params={"status": Status.SUBMITTED.value, "comment": "Try to approve"},
    )

    assert response.status_code == 400
    assert (
        "invalid status transition, status should be in_progress, "
        "completed or rejected"
    ) in response.json()["detail"].lower()


def test_admin_cannot_submit_requester(
    client,
    dashboard_admin,
    requests_with_tracking,
    auth_as,
):
    """
    Only APPROVED requests can be assigned.
    """
    admin = dashboard_admin["admin1"]
    requests = requests_with_tracking["requests"]
    request = requests[0]
    request.current_status = Status.SUBMITTED

    auth_as(admin)

    response = client.patch(
        f"{API_PREFIX}/{request.id}",
        params={"status": Status.SUBMITTED.value, "comment": "Try to submit"},
    )

    assert response.status_code == 400
    assert (
        "invalid status transition, status should be in_progress, "
        "completed or rejected"
    ) in response.json()["detail"].lower()


def test_cannot_process_rejected_request(
    client,
    dashboard_admin,
    requests_with_tracking,
    auth_as,
):
    """
    Only APPROVED requests can be assigned.
    """
    admin = dashboard_admin["admin1"]
    requests = requests_with_tracking["requests"]
    request = requests[1]
    request.current_status = Status.REJECTED

    auth_as(admin)

    response = client.patch(
        f"{API_PREFIX}/{request.id}",
        params={"status": Status.IN_PROGRESS.value, "comment": "Start work"},
    )

    assert response.status_code == 400
    assert "request already rejected" in response.json()["detail"].lower()


def test_cannot_process_completed_request(
    client,
    dashboard_admin,
    requests_with_tracking,
    auth_as,
):
    """
    Only APPROVED requests can be assigned.
    """
    admin = dashboard_admin["admin1"]
    requests = requests_with_tracking["requests"]
    request = requests[1]
    request.current_status = Status.COMPLETED

    auth_as(admin)

    response = client.patch(
        f"{API_PREFIX}/{request.id}",
        params={"status": Status.IN_PROGRESS.value, "comment": "Start work"},
    )

    assert response.status_code == 400
    assert "request already completed" in response.json()["detail"].lower()


def test_admin_cannot_assign_twice(
    client, dashboard_admin, requests_with_tracking, auth_as
):
    admin = dashboard_admin["admin1"]
    request = requests_with_tracking["requests"][1]

    auth_as(admin)

    client.patch(
        f"{API_PREFIX}/{request.id}",
        params={"status": Status.IN_PROGRESS.value},
    )

    response = client.patch(
        f"{API_PREFIX}/{request.id}",
        params={"status": Status.IN_PROGRESS.value},
    )

    assert response.status_code == 400
    assert "already assigned" in response.json()["detail"].lower()


def test_cannot_complete_without_assigning(
    client, dashboard_admin, requests_with_tracking, auth_as
):
    admin = dashboard_admin["admin1"]
    request = requests_with_tracking["requests"][1]  # APPROVED

    auth_as(admin)

    response = client.patch(
        f"{API_PREFIX}/{request.id}",
        params={"status": Status.COMPLETED.value},
    )

    assert response.status_code == 403
    assert "assign the request to yourself first" in response.json()["detail"].lower()
