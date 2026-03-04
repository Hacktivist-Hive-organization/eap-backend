import pytest

from app.common.enums import Status
from app.core.config import settings
from app.models import DBRequestTracking

API_PREFIX = f"{settings.API_V1_PREFIX}/requests"


@pytest.fixture
def submitted_request_with_tracking(db_session, users, seeded_requests_for_user):
    req = seeded_requests_for_user[1]
    approver = users["user2"]
    tracking = DBRequestTracking(
        request_id=req.id,
        user_id=approver.id,
        status=Status.SUBMITTED,
        comment="Initial submission",
    )
    db_session.add(tracking)
    db_session.commit()
    return req


def test_process_request_approve_success(
    client, users, auth_as, submitted_request_with_tracking
):
    approver = users["user2"]
    auth_as(approver)

    request_id = submitted_request_with_tracking.id
    response = client.post(
        f"{API_PREFIX}/{request_id}/process?status=approved&comment=Looks good"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["current_status"] == Status.APPROVED


def test_process_request_reject_success(
    client, users, auth_as, submitted_request_with_tracking
):
    approver = users["user2"]
    auth_as(approver)

    request_id = submitted_request_with_tracking.id
    response = client.post(
        f"{API_PREFIX}/{request_id}/process?status=rejected&comment=Insufficient info"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["current_status"] == Status.REJECTED


def test_process_request_reject_missing_comment(
    client, users, auth_as, submitted_request_with_tracking
):
    approver = users["user2"]
    auth_as(approver)

    request_id = submitted_request_with_tracking.id
    response = client.post(f"{API_PREFIX}/{request_id}/process?status=rejected")

    assert response.status_code == 400
    assert response.json()["detail"] == "Comment is mandatory for rejection"


def test_process_request_cancel_success(
    client, users, auth_as, submitted_request_with_tracking
):
    approver = users["user2"]
    auth_as(approver)

    request_id = submitted_request_with_tracking.id
    response = client.post(
        f"{API_PREFIX}/{request_id}/process?status=cancelled&comment=Changed my mind"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["current_status"] == Status.CANCELLED


def test_process_request_unauthorized(
    client, users, auth_as, submitted_request_with_tracking
):
    other_user = users["user1"]
    auth_as(other_user)  # user1 is not assigned to the tracking record

    request_id = submitted_request_with_tracking.id
    response = client.post(f"{API_PREFIX}/{request_id}/process?status=approved")

    assert response.status_code == 403
    assert "not authorized to process this request" in response.json()["detail"]


def test_process_request_invalid_next_status(
    client, users, auth_as, submitted_request_with_tracking
):
    approver = users["user2"]
    auth_as(approver)

    request_id = submitted_request_with_tracking.id
    response = client.post(f"{API_PREFIX}/{request_id}/process?status=draft")

    assert response.status_code == 400
    assert "Invalid status transition" in response.json()["detail"]


def test_process_request_invalid_current_status(
    client, users, auth_as, seeded_requests_for_user, db_session
):
    # draft is index 0
    req = seeded_requests_for_user[0]
    approver = users["user2"]
    auth_as(approver)

    # Add tracking
    tracking = DBRequestTracking(
        request_id=req.id, user_id=approver.id, status=Status.DRAFT, comment="Drafting"
    )
    db_session.add(tracking)
    db_session.commit()

    response = client.post(f"{API_PREFIX}/{req.id}/process?status=approved")

    assert response.status_code == 400
    assert (
        "cannot be approved because it is in draft status" in response.json()["detail"]
    )
