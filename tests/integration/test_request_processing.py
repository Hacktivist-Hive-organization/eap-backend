# tests/integration/requests/test_request_transitions_atomic.py

import pytest

from app.common.enums import Status, UserRole
from app.models import DBRequestTracking
from app.repositories.request_repository import RequestRepository
from app.repositories.request_tracking_repository import RequestTrackingRepository
from app.services.email_service import EmailService
from app.services.request_tracking_service import RequestTrackingService


@pytest.fixture
def tracking_service(db_session, real_email_manager):
    req_repo = RequestRepository(db_session)
    track_repo = RequestTrackingRepository(db_session)
    email_service = EmailService(manager=real_email_manager)
    return RequestTrackingService(track_repo, req_repo, email_service)


@pytest.fixture
def users_for_test(users):
    return {
        UserRole.REQUESTER: users["user1"],
        UserRole.APPROVER: users["user2"],
        UserRole.ADMIN: users["admin1"],
    }


def test_transition_draft_to_submitted(
    db_session, tracking_service, users_for_test, seeded_requests_for_user
):
    requester = users_for_test[UserRole.REQUESTER]
    request = seeded_requests_for_user[0]  # DRAFT request

    tracking_service.transition_request(
        request=request,
        next_status=Status.SUBMITTED,
        current_user=requester,
        comment="Submitting request",
    )

    db_session.refresh(request)
    assert request.current_status == Status.SUBMITTED

    tracking = (
        db_session.query(DBRequestTracking)
        .filter_by(request_id=request.id)
        .order_by(DBRequestTracking.created_at.desc())
        .first()
    )
    assert tracking.status == Status.SUBMITTED
    assert tracking.user_id == requester.id


def test_transition_submitted_to_cancelled(
    db_session, tracking_service, users_for_test, seeded_requests_for_user
):
    requester = users_for_test[UserRole.REQUESTER]
    request = seeded_requests_for_user[1]  # SUBMITTED request

    tracking_service.transition_request(
        request=request,
        next_status=Status.CANCELLED,
        current_user=requester,
        comment="Cancelling request",
    )

    db_session.refresh(request)
    assert request.current_status == Status.CANCELLED

    tracking = (
        db_session.query(DBRequestTracking)
        .filter_by(request_id=request.id)
        .order_by(DBRequestTracking.created_at.desc())
        .first()
    )
    assert tracking.status == Status.CANCELLED
    assert tracking.user_id == requester.id
