# app/services/request_tracking_service.py

from fastapi import BackgroundTasks
from starlette import status

from app.common.enums import UserRole
from app.common.exceptions import BusinessException
from app.common.request_workflow.request_transition_validator import (
    RequestTransitionValidator,
)
from app.common.security_models import CurrentUser
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
        self, request_id: int, current_user: CurrentUser
    ):
        request = self.request_repo.get_request_details(request_id)
        if not request:
            raise BusinessException(
                message="Request not found",
                status_code=status.HTTP_404_NOT_FOUND,
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

    async def transition_request(
        self,
        request,
        next_status,
        current_user: CurrentUser,
        comment: str | None = None,
        background_tasks: BackgroundTasks | None = None,
    ):
        rule = self.transition_validator.validate(
            request=request,
            next_status=next_status,
            user_id=current_user.id,
            comment=comment,
        )
        self.repo.create(
            comment=comment or "",
            request_id=request.id,
            status=next_status,
            user_id=current_user.id,
        )
        self.request_repo.update_request_status(request, next_status)

        if background_tasks and rule.get("notify_roles"):
            notify_users = set()
            if UserRole.REQUESTER in rule["notify_roles"]:
                notify_users.add(request.requester)
            if UserRole.APPROVER in rule["notify_roles"]:
                approvers = [
                    t.user
                    for t in request.req_tracking
                    if t.user.role == UserRole.APPROVER
                ]
                notify_users.update(approvers)
            if UserRole.ADMIN in rule["notify_roles"]:
                admins = [
                    t.user
                    for t in request.req_tracking
                    if t.user.role == UserRole.ADMIN
                ]
                notify_users.update(admins)

            for user in notify_users:
                email = getattr(user, "email", None)
                if email:
                    template = rule.get("template", "REQUEST_UPDATE")
                    background_tasks.add_task(
                        self.email_service.send_email,
                        to=email,
                        subject=f"Request {next_status.value}",
                        body=f"Request {request.id} has been {next_status.value}. Template: {template}",
                    )

        return self.repo.get_request_tracking_by_request_id(request.id)
