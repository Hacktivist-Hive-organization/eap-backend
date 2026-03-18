# tests/integration/requests/test_request_transitions.py

import asyncio

from fastapi import BackgroundTasks

from app.common.enums import Status
from app.common.security_models import CurrentUser
from app.infrastructure.email.manager import EmailManager
from app.repositories.request_repository import RequestRepository
from app.repositories.request_tracking_repository import RequestTrackingRepository
from app.services.email_service import EmailService
from app.services.request_tracking_service import RequestTrackingService


def get_service(db_session):
    request_repo = RequestRepository(db_session)
    tracking_repo = RequestTrackingRepository(db_session)

    email_manager = EmailManager()
    email_service = EmailService(email_manager)

    return RequestTrackingService(
        repo=tracking_repo,
        request_repo=request_repo,
        email_service=email_service,
    )


def create_request(
    db_session,
    user,
    seeded_types,
    status=Status.DRAFT,
):
    req_repo = RequestRepository(db_session)
    req = req_repo.create(
        request=type(
            "Req",
            (),
            dict(
                type_id=seeded_types["hardware"].id,
                subtype_id=seeded_types["laptop"].id,
                title="Test Request",
                description="Valid description long enough",
                business_justification="Valid justification long enough",
                priority="medium",
            ),
        )(),
        current_user_id=user.id,
        current_status=status,
    )
    return req


def assign_approver(db_session, request, approver):
    from app.models import DBRequestTracking

    tracking = DBRequestTracking(
        request_id=request.id,
        user_id=approver.id,
        status=Status.SUBMITTED,
    )
    db_session.add(tracking)
    db_session.commit()


def assign_admin(db_session, request, admin):
    from app.models import DBRequestTracking

    tracking = DBRequestTracking(
        request_id=request.id, user_id=admin.id, status=request.current_status
    )
    db_session.add(tracking)
    db_session.commit()


def run(coro, background_tasks: BackgroundTasks):
    async def runner():
        result = await coro

        for task in background_tasks.tasks:
            await task()

        return result

    return asyncio.run(runner())


def test_draft_to_submitted(db_session, users, seeded_request_types):
    service = get_service(db_session)
    bg = BackgroundTasks()

    requester = users["user1"]
    request = create_request(
        db_session,
        requester,
        seeded_request_types,
        Status.DRAFT,
    )
    current_user = CurrentUser(id=requester.id, role=requester.role)

    run(
        service.transition_request(
            request, Status.SUBMITTED, current_user, background_tasks=bg
        ),
        bg,
    )

    assert request.current_status == Status.SUBMITTED


def test_submitted_to_cancelled(db_session, users, seeded_request_types):
    service = get_service(db_session)
    bg = BackgroundTasks()

    requester = users["user1"]
    request = create_request(
        db_session,
        requester,
        seeded_request_types,
        Status.SUBMITTED,
    )
    current_user = CurrentUser(id=requester.id, role=requester.role)

    run(
        service.transition_request(
            request, Status.CANCELLED, current_user, background_tasks=bg
        ),
        bg,
    )

    assert request.current_status == Status.CANCELLED


def test_submitted_to_approved(
    db_session, dashboard_approvers, users, seeded_request_types
):
    service = get_service(db_session)
    bg = BackgroundTasks()

    approver = dashboard_approvers["dashboard_approver1"]
    request = create_request(
        db_session,
        users["user1"],
        seeded_request_types,
        Status.SUBMITTED,
    )
    assign_approver(db_session, request, approver)
    current_user = CurrentUser(id=approver.id, role=approver.role)

    run(
        service.transition_request(
            request, Status.APPROVED, current_user, background_tasks=bg
        ),
        bg,
    )

    assert request.current_status == Status.APPROVED


def test_submitted_to_rejected(
    db_session, dashboard_approvers, users, seeded_request_types
):
    service = get_service(db_session)
    bg = BackgroundTasks()

    approver = dashboard_approvers["dashboard_approver1"]
    request = create_request(
        db_session,
        users["user1"],
        seeded_request_types,
        Status.SUBMITTED,
    )
    assign_approver(db_session, request, approver)
    current_user = CurrentUser(id=approver.id, role=approver.role)

    run(
        service.transition_request(
            request,
            Status.REJECTED,
            current_user,
            comment="Rejected",
            background_tasks=bg,
        ),
        bg,
    )

    assert request.current_status == Status.REJECTED


def test_approved_to_in_progress(
    db_session, dashboard_admin, users, seeded_request_types
):
    service = get_service(db_session)
    bg = BackgroundTasks()

    admin = dashboard_admin["admin1"]
    request = create_request(
        db_session,
        users["user1"],
        seeded_request_types,
        Status.APPROVED,
    )
    assign_admin(db_session, request, admin)
    current_user = CurrentUser(id=admin.id, role=admin.role)

    run(
        service.transition_request(
            request, Status.IN_PROGRESS, current_user, background_tasks=bg
        ),
        bg,
    )

    assert request.current_status == Status.IN_PROGRESS


def test_in_progress_to_completed(
    db_session, dashboard_admin, users, seeded_request_types
):
    service = get_service(db_session)
    bg = BackgroundTasks()

    admin = dashboard_admin["admin1"]
    request = create_request(
        db_session,
        users["user1"],
        seeded_request_types,
        Status.IN_PROGRESS,
    )
    assign_admin(db_session, request, admin)
    current_user = CurrentUser(id=admin.id, role=admin.role)

    run(
        service.transition_request(
            request, Status.COMPLETED, current_user, background_tasks=bg
        ),
        bg,
    )

    assert request.current_status == Status.COMPLETED


def test_in_progress_to_rejected(
    db_session, dashboard_admin, users, seeded_request_types
):
    service = get_service(db_session)
    bg = BackgroundTasks()

    admin = dashboard_admin["admin1"]
    request = create_request(
        db_session,
        users["user1"],
        seeded_request_types,
        Status.IN_PROGRESS,
    )
    assign_admin(db_session, request, admin)
    current_user = CurrentUser(id=admin.id, role=admin.role)

    run(
        service.transition_request(
            request,
            Status.REJECTED,
            current_user,
            comment="Rejected",
            background_tasks=bg,
        ),
        bg,
    )

    assert request.current_status == Status.REJECTED
