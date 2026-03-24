# tests/integration/test_reopen_cancelled_request.py

import pytest

from app.common.enums import Status
from app.core.config import settings
from app.models import DBRequestTracking

API_PREFIX = f"{settings.API_V1_PREFIX}/requests"


@pytest.fixture
def cancel_request_with_tracking(
    db_session, users, seeded_requests_for_user, dashboard_approvers
):
    req = seeded_requests_for_user[1]
    user = users["user1"]
    tracking = DBRequestTracking(
        request_id=req.id,
        user_id=user.id,
        status=Status.CANCELLED,
        comment="Cancel Request",
    )
    req.current_status = Status.CANCELLED

    db_session.add(tracking)
    db_session.commit()

    return req


def test_reopen_cancelled_request_success(
    client, users, auth_as, cancel_request_with_tracking
):
    user = users["user1"]
    auth_as(user)

    request_id = cancel_request_with_tracking.id
    response = client.patch(f"{API_PREFIX}/{request_id}/reopen")

    assert response.status_code == 200
    body = response.json()
    assert body["current_status"] == Status.DRAFT


def test_not_authorized_cancel_request(
    client, users, auth_as, cancel_request_with_tracking
):
    user = users["user2"]
    auth_as(user)

    request_id = cancel_request_with_tracking.id
    response = client.patch(f"{API_PREFIX}/{request_id}/reopen")

    assert response.status_code == 403


def test_request_is_not_cancelled(client, users, auth_as, seeded_requests_for_user):
    user = users["user1"]
    auth_as(user)

    req = seeded_requests_for_user[1]
    response = client.patch(f"{API_PREFIX}/{req.id}/reopen")

    assert response.status_code == 403
