# tests/integration/test_approver_requests.py
import os

import pytest

from app.common.enums import Status
from app.core.config import settings
from app.models import DBRequestTracking

API_PREFIX = f"{settings.API_V1_PREFIX}/approver/requests"

pytestmark = pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason="DbUser.username not ready, skipping temporarily in CI",
)


# -------------------------------------------------
# Fixture: assign requests to dashboard approver
# -------------------------------------------------
@pytest.fixture
def assigned_requests(
    db_session,
    dashboard_approvers,
    seeded_requests_for_user,
):
    """
    Assign requests with explicit statuses:
    - 2 SUBMITTED
    - 2 APPROVED
    - 1 REJECTED
    """

    approver = dashboard_approvers["dashboard_approver1"]

    # Force deterministic statuses
    seeded_requests_for_user[0].current_status = Status.SUBMITTED
    seeded_requests_for_user[1].current_status = Status.SUBMITTED
    seeded_requests_for_user[2].current_status = Status.APPROVED
    seeded_requests_for_user[3].current_status = Status.APPROVED
    seeded_requests_for_user[4].current_status = Status.REJECTED

    db_session.flush()

    for req in seeded_requests_for_user:
        db_session.add(
            DBRequestTracking(
                request_id=req.id,
                user_id=approver.id,
                status=req.current_status,
                comment="Assigned for dashboard test",
            )
        )

    db_session.commit()

    return {
        "approver": approver,
        "requests": seeded_requests_for_user,
    }


def filter_requests_by_status(requests, statuses):
    return [r for r in requests if r.current_status in statuses]


# -------------------------------------------------
# Tests
# -------------------------------------------------


def test_get_assigned_requests_success(
    client,
    auth_as,
    assigned_requests,
):
    approver = assigned_requests["approver"]
    auth_as(approver)

    response = client.get(API_PREFIX)

    assert response.status_code == 200
    data = response.json()

    returned_ids = {r["id"] for r in data}
    expected_ids = {r.id for r in assigned_requests["requests"]}

    assert returned_ids == expected_ids


def test_get_assigned_requests_are_ordered_by_created_desc(
    client,
    auth_as,
    assigned_requests,
):
    approver = assigned_requests["approver"]
    auth_as(approver)

    response = client.get(API_PREFIX)

    assert response.status_code == 200
    data = response.json()

    # Extract created_at from response
    created_dates = [r["created_at"] for r in data]

    # Ensure sorted descending
    assert created_dates == sorted(created_dates, reverse=True)


def test_get_assigned_requests_filter_returns_empty_list(
    client,
    auth_as,
    assigned_requests,
):
    approver = assigned_requests["approver"]
    auth_as(approver)

    # Choose a status you know does NOT exist in seeded data
    response = client.get(f"{API_PREFIX}?statuses={Status.CANCELLED.value}")

    assert response.status_code == 200
    assert response.json() == []


def test_get_assigned_requests_invalid_status_returns_422(
    client,
    auth_as,
    assigned_requests,
):
    approver = assigned_requests["approver"]
    auth_as(approver)

    response = client.get(f"{API_PREFIX}?statuses=INVALID_STATUS")

    assert response.status_code == 422


def test_get_assigned_requests_filter_by_one_status(
    client,
    auth_as,
    assigned_requests,
):
    approver = assigned_requests["approver"]
    auth_as(approver)

    statuses = {Status.SUBMITTED}

    response = client.get(f"{API_PREFIX}?statuses={Status.SUBMITTED.value}")

    assert response.status_code == 200
    data = response.json()

    expected = filter_requests_by_status(
        assigned_requests["requests"],
        statuses,
    )

    assert len(data) == len(expected)

    returned_ids = {r["id"] for r in data}
    expected_ids = {r.id for r in expected}

    assert returned_ids == expected_ids


def test_get_assigned_requests_filter_by_two_statuses(
    client,
    auth_as,
    assigned_requests,
):
    approver = assigned_requests["approver"]
    auth_as(approver)

    statuses = {Status.SUBMITTED, Status.APPROVED}

    response = client.get(
        f"{API_PREFIX}?statuses={Status.SUBMITTED.value}"
        f"&statuses={Status.APPROVED.value}"
    )

    assert response.status_code == 200
    data = response.json()

    expected = filter_requests_by_status(
        assigned_requests["requests"],
        statuses,
    )

    assert len(data) == len(expected)

    returned_ids = {r["id"] for r in data}
    expected_ids = {r.id for r in expected}

    assert returned_ids == expected_ids


def test_get_assigned_requests_without_filter_returns_all(
    client,
    auth_as,
    assigned_requests,
):
    approver = assigned_requests["approver"]
    auth_as(approver)

    response = client.get(API_PREFIX)

    assert response.status_code == 200
    data = response.json()

    expected = assigned_requests["requests"]

    assert len(data) == len(expected)

    returned_ids = {r["id"] for r in data}
    expected_ids = {r.id for r in expected}

    assert returned_ids == expected_ids


def test_get_assigned_requests_empty_for_other_approver(
    client,
    auth_as,
    dashboard_approvers,
):
    ## Nothing is assigned to "dashboard_approver2" yet
    other_approver = dashboard_approvers["dashboard_approver2"]
    auth_as(other_approver)

    response = client.get(API_PREFIX)

    assert response.status_code == 200
    assert response.json() == []


def test_get_assigned_requests_forbidden_for_non_approver(
    client,
    auth_as,
    users,
):
    normal_user = users["user1"]
    auth_as(normal_user)

    response = client.get(API_PREFIX)

    assert response.status_code == 403
    assert response.json()["detail"] == "User is not an approver"
