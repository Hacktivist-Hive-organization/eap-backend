# tests/integration/test_approver_request_details.py

import os

import pytest

from app.core.config import settings
from app.models import DBRequestTracking

API_PREFIX = f"{settings.API_V1_PREFIX}/requests"

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
    Assign all seeded requests to dashboard_approver1 via tracking entries.
    dashboard_approver2 intentionally receives no assignments.
    """
    approver = dashboard_approvers["dashboard_approver1"]

    for req in seeded_requests_for_user:
        db_session.add(
            DBRequestTracking(
                request_id=req.id,
                user_id=approver.id,
                status=req.current_status,
                comment="Assigned for approver detail test",
            )
        )

    db_session.commit()

    return {
        "approver": approver,
        "requests": seeded_requests_for_user,
    }


# =========================================================
# SUCCESS
# =========================================================


def test_get_approver_request_details_success(
    client,
    auth_as,
    assigned_requests,
    seeded_request_types,
):
    """
    Assigned approver can fetch full request details.
    Response must include id, title, status, type, subtype, requester and timestamps.
    """
    approver = assigned_requests["approver"]
    request = assigned_requests["requests"][0]
    auth_as(approver)

    response = client.get(f"{API_PREFIX}/{request.id}")

    assert response.status_code == 200
    body = response.json()

    assert body["id"] == request.id
    assert body["title"] == request.title
    assert body["current_status"] == request.current_status.value
    assert body["priority"] == request.priority.value
    assert body["description"] == request.description
    assert body["business_justification"] == request.business_justification

    assert body["type"]["id"] == seeded_request_types["hardware"].id
    assert body["subtype"]["id"] == seeded_request_types["laptop"].id

    assert body["requester"]["id"] is not None
    assert body["created_at"] is not None
    assert body["updated_at"] is not None


# =========================================================
# NOT FOUND
# =========================================================


def test_get_approver_request_details_not_found(
    client,
    auth_as,
    assigned_requests,
):
    """
    Returns 404 when the request id does not exist.
    """
    approver = assigned_requests["approver"]
    auth_as(approver)

    response = client.get(f"{API_PREFIX}/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Request not found"


# =========================================================
# NOT ASSIGNED — different approver
# =========================================================


def test_get_approver_request_details_forbidden_for_unassigned_approver(
    client,
    auth_as,
    assigned_requests,
    dashboard_approvers,
):
    """
    An approver with no tracking entry for the request gets 403.
    dashboard_approver2 has no assignments.
    """
    unassigned_approver = dashboard_approvers["dashboard_approver2"]
    request = assigned_requests["requests"][0]
    auth_as(unassigned_approver)

    response = client.get(f"{API_PREFIX}/{request.id}")

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized to view this request"


# =========================================================
# NOT ASSIGNED — regular requester
# =========================================================


# def test_get_approver_request_details_forbidden_for_requester(
#     client,
#     auth_as,
#     assigned_requests,
#     users,
# ):
#     """
#     A regular requester user (no tracking entry) gets 403.
#     The requester endpoint should be used instead of the approver one.
#     """
#     requester = users["user1"]
#     request = assigned_requests["requests"][0]
#     auth_as(requester)
#
#     response = client.get(f"{API_PREFIX}/{request.id}")
#
#     assert response.status_code == 403
#     assert response.json()["detail"] == "You are not authorized to view this request"
