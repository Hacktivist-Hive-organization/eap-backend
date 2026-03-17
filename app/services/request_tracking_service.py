# app/services/request_tracking_service.py

from typing import List, Optional

from fastapi import BackgroundTasks
from starlette import status

from app.common.enums import Status, UserRole
from app.common.exceptions import BusinessException
from app.common.request_workflow.request_transition_validator import (
    RequestTransitionValidator,
)
from app.common.security_models import CurrentUser
from app.core.config import settings
from app.repositories import RequestRepository, RequestTrackingRepository
from app.services.email_service import EmailService


class RequestTrackingService:

    def __init__(
        self,
        repo: RequestTrackingRepository,
        request_repo: RequestRepository,
        email_service: EmailService,
    ):
        self.repo = repo
        self.request_repo = request_repo
        self.email_service = email_service
        self.transition_validator = RequestTransitionValidator(repo)

    def get_request_tracking_by_request_id(
        self,
        request_id: int,
        current_user: CurrentUser,
    ):
        request = self.request_repo.get_request_details(request_id)
        if not request:
            raise BusinessException(
                message="Request not found", status_code=status.HTTP_404_NOT_FOUND
            )
        is_requester = request.requester_id == current_user.id
        is_approver = bool(
            self.repo.get_tracking_by_request_user_id(request_id, current_user.id)
        )
        if not (is_requester or is_approver or current_user.role == UserRole.ADMIN):
            raise BusinessException(
                message="You do not have permission to track this request",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return self.repo.get_request_tracking_by_request_id(request_id)

    def process_request(
        self,
        request_id: int,
        status_in: Status,
        user_id: int,
        comment: str,
        background_tasks: Optional[BackgroundTasks] = None,
    ):
        request = self.request_repo.get_request_details(request_id)
        if not request:
            raise BusinessException(
                message="Request not found", status_code=status.HTTP_404_NOT_FOUND
            )

        rule = self.transition_validator.validate(request, status_in, user_id, comment)

        try:
            self.request_repo.update_request_status(request, status_in, commit=False)
            self.repo.create(comment, request_id, status_in, user_id, commit=False)
            self.repo.db.commit()
        except Exception:
            self.repo.db.rollback()
            raise BusinessException(
                message="Database error, Please contact your administrator",
                status_code=status.HTTP_417_EXPECTATION_FAILED,
            )

        template_name = rule.get("template")
        notify_roles = rule.get("notify_roles", [])

        if background_tasks and template_name and notify_roles:
            recipients = self._get_notification_emails(request, notify_roles)
            for email in recipients:
                subject = f"Request {status_in.value.capitalize()} - REQ-{request.id} - {request.title}"
                body = self._render_email_body(request, status_in, template_name)
                background_tasks.add_task(
                    self.email_service.send_email,
                    to=email,
                    subject=subject,
                    body=body,
                )

        return request

    def get_request_by_id_for_approver(self, request_id: int, user_id: int):
        request = self.request_repo.get_request_details(request_id)
        if not request:
            raise BusinessException(
                message="Request not found", status_code=status.HTTP_404_NOT_FOUND
            )
        request_tracking = self.repo.get_tracking_by_request_user_id(
            request_id, user_id
        )
        if not request_tracking:
            raise BusinessException(
                message="You are not authorized to view this request",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return request

    def get_requests_for_approver(
        self, current_user, statuses: Optional[List[Status]] = None
    ) -> list:
        if current_user.role != UserRole.APPROVER:
            raise BusinessException(
                message="User is not an approver", status_code=status.HTTP_403_FORBIDDEN
            )
        return self.repo.get_requests_for_approver(
            approver_id=current_user.id, statuses=statuses
        )

    def _render_email_body(self, request, status_in: Status, template_name: str) -> str:
        from app.infrastructure.email.templates import TEMPLATE_REGISTRY

        template = TEMPLATE_REGISTRY.get(template_name)
        if not template:
            return ""

        link = f"{settings.FRONTEND_URL}/dashboard/all?requestId={request.id}"
        requester = request.requester

        return template.substitute(
            request_code=f"REQ-{request.id}",
            request_title=request.title,
            user_name=f"{requester.first_name} {requester.last_name}",
            request_id=request.id,
            request_type=f"{request.type.name} > {request.subtype.name}",
            priority=request.priority.value,
            submitted_at=request.created_at.strftime("%B %d, %Y at %I:%M %p"),
            status=status_in.value,
            link=link,
        )

    def _get_notification_emails(self, request, roles: List[UserRole]) -> List[str]:
        emails = set()
        if UserRole.REQUESTER in roles and request.requester:
            emails.add(request.requester.email)
        for tracking in request.req_tracking:
            if tracking.user and tracking.user.role in roles:
                emails.add(tracking.user.email)
        return list(emails)
