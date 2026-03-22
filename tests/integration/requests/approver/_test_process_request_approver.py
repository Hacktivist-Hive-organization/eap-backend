# tests/integration/requests/test_process_request_approver.py

import pytest
from fastapi.testclient import TestClient

from app.common.enums import Status
from app.models.db_request import DBRequest
from app.models.db_user import DbUser

# -------------------- HELPERS --------------------


def _get_submitted_request(requests):
    return next(r for r in requests if r.current_status == Status.SUBMITTED)


def _get_approved_request(requests):
    return next(r for r in requests if r.current_status == Status.APPROVED)


def _get_approver(approvers_dict):
    return next(iter(approvers_dict.values()))


def _assign_approver(db_session, request, approver):
    from app.models.db_request_tracking import DBRequestTracking

    tracking = DBRequestTracking(
        request_id=request.id,
        user_id=approver.id,
        status=Status.SUBMITTED,
        comment="assigned to approver",
    )
    db_session.add(tracking)
    db_session.commit()


# -------------------- TESTS --------------------


def test_approver_can_approve_request(
    client: TestClient,
    db_session,
    seeded_requests_for_user,
    dashboard_approvers,
    auth_as,
):
    request = _get_submitted_request(seeded_requests_for_user)
    approver = _get_approver(dashboard_approvers)

    _assign_approver(db_session, request, approver)
    auth_as(approver)

    response = client.patch(
        f"/api/v1/requests/{request.id}/process",
        params={"status": Status.APPROVED.value},
    )

    assert response.status_code == 200
    assert response.json()["current_status"] == Status.APPROVED.value


def test_approver_can_reject_request(
    client: TestClient,
    db_session,
    seeded_requests_for_user,
    dashboard_approvers,
    auth_as,
):
    request = _get_submitted_request(seeded_requests_for_user)
    approver = _get_approver(dashboard_approvers)

    _assign_approver(db_session, request, approver)
    auth_as(approver)

    response = client.patch(
        f"/api/v1/requests/{request.id}/process",
        params={"status": Status.REJECTED.value, "comment": "Reject reason"},
    )

    assert response.status_code == 200
    assert response.json()["current_status"] == Status.REJECTED.value


def test_approver_without_assignment_should_fail(
    client: TestClient,
    seeded_requests_for_user,
    dashboard_approvers,
    auth_as,
):
    request = _get_submitted_request(seeded_requests_for_user)
    approver = _get_approver(dashboard_approvers)

    auth_as(approver)  # no assignment

    response = client.patch(
        f"/api/v1/requests/{request.id}/process",
        params={"status": Status.APPROVED.value},
    )

    assert response.status_code == 403
    assert "approver" in response.json()["detail"].lower()


def test_approver_invalid_transition_should_fail(
    client: TestClient,
    db_session,
    seeded_requests_for_user,
    dashboard_approvers,
    auth_as,
):
    request = _get_submitted_request(seeded_requests_for_user)
    approver = _get_approver(dashboard_approvers)

    _assign_approver(db_session, request, approver)
    auth_as(approver)

    # Attempt invalid transition (APPROVER can't CANCEL from SUBMITTED)
    response = client.patch(
        f"/api/v1/requests/{request.id}/process",
        params={"status": Status.CANCELLED.value},
    )

    assert response.status_code == 403
    assert "approver" in response.json()["detail"].lower()


def test_approver_requires_comment_for_reject(
    client: TestClient,
    db_session,
    seeded_requests_for_user,
    dashboard_approvers,
    auth_as,
):
    request = _get_submitted_request(seeded_requests_for_user)
    approver = _get_approver(dashboard_approvers)

    _assign_approver(db_session, request, approver)
    auth_as(approver)

    # Attempt to reject without comment
    response = client.patch(
        f"/api/v1/requests/{request.id}/process",
        params={"status": Status.REJECTED.value},
    )

    assert response.status_code == 400
    assert "comment" in response.json()["detail"].lower()
