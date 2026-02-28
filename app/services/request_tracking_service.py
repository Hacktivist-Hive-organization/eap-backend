# app/services/request_tracking_service.py

import asyncio
import time
from typing import List, Optional

from fastapi import BackgroundTasks
from starlette import status

from app.common.enums import Status, UserRole
from app.common.exceptions import BusinessException
from app.common.request_state_config import REQUEST_STATE_CONFIG
from app.common.request_state_machine import RequestStateMachine
from app.core.config import settings
from app.infrastructure.email.manager import EmailManager
from app.infrastructure.email.templates import (
    REQUEST_APPROVED,
    REQUEST_REJECTED,
    REQUEST_SUBMITTED,
)
from app.repositories import RequestRepository, RequestTrackingRepository


class RequestTrackingService:

    def __init__(
        self,
        repo: RequestTrackingRepository,
        request_repo: RequestRepository,
        email_manager: EmailManager,
    ):
        self.repo = repo
        self.request_repo = request_repo
        self.email_manager = email_manager

    def get_request_tracking_by_request_id(self, request_id: int, user_id: int):
        request = self.request_repo.get_request_details(request_id)
        if not request:
            raise BusinessException(
                message="Request not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        is_requester = request.requester_id == user_id
        is_approver = bool(
            self.repo.get_tracking_by_request_user_id(request_id, user_id)
        )

        if not (is_requester or is_approver):
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
        comment: Optional[str],
        background_tasks: Optional[BackgroundTasks] = None,
    ):
        request = self.request_repo.get_request_details(request_id)
        if not request:
            raise BusinessException(
                message="Request not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        request_tracking = self.repo.get_tracking_by_request_user_id(
            request_id, user_id
        )
        is_requester = request.requester_id == user_id
        is_assigned_approver = bool(request_tracking)

        if status_in == Status.CANCELLED:
            if not is_requester and not is_assigned_approver:
                raise BusinessException(
                    message="You are not authorized to process this request",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
        elif status_in in [Status.APPROVED, Status.REJECTED]:
            if not is_assigned_approver:
                raise BusinessException(
                    message="You are not authorized to process this request",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
        else:
            raise BusinessException(
                message="Invalid status transition",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if (
            status_in in [Status.APPROVED, Status.REJECTED]
            and request.current_status != Status.SUBMITTED
        ):
            raise BusinessException(
                message=f"Request cannot be {status_in.value} because it is in {request.current_status.value} status",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if status_in == Status.REJECTED and not comment:
            raise BusinessException(
                message="Comment is mandatory for rejection",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

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

        if background_tasks:
            template = (
                REQUEST_REJECTED
                if status_in == Status.REJECTED
                else (
                    REQUEST_APPROVED
                    if status_in == Status.APPROVED
                    else REQUEST_SUBMITTED
                )
            )
            background_tasks.add_task(
                self._send_email_task, request, status_in, template
            )

        return request

    def get_request_by_id_for_approver(self, request_id: int, user_id: int):
        request = self.request_repo.get_request_details(request_id)
        if not request:
            raise BusinessException(
                message="Request not found",
                status_code=status.HTTP_404_NOT_FOUND,
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
                message="User is not an approver",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        return self.repo.get_requests_for_approver(
            approver_id=current_user.id, statuses=statuses
        )

    def _send_email_task(self, request, status_in: Status, template):
        recipients: List[str] = []

        if status_in == Status.APPROVED or status_in == Status.REJECTED:
            recipients.append(request.requester.email)
            for tracking in request.trackings:
                recipients.append(tracking.user.email)
        elif status_in == Status.SUBMITTED:
            for tracking in request.trackings:
                recipients.append(tracking.user.email)

        if not recipients:
            return

        link = f"{settings.FRONTEND_URL}/requests/{request.id}"

        email_body = template.substitute(
            request_code=f"REQ-{request.id}",
            request_title=request.title,
            user_name=f"{request.requester.first_name} {request.requester.last_name}",
            request_id=request.id,
            request_type=f"{request.type.name} > {request.subtype.name}",
            priority=request.priority.value,
            submitted_at=request.created_at.strftime("%B %d, %Y at %I:%M %p"),
            status=status_in.value,
            link=link,
        )

        subject_prefix = (
            "Request Rejected"
            if status_in == Status.REJECTED
            else (
                "Request Approved"
                if status_in == Status.APPROVED
                else "Request Submitted"
            )
        )

        time.sleep(10)

        asyncio.run(
            self.email_manager.send_email(
                to=",".join(recipients),
                subject=f"{subject_prefix} - REQ-{request.id} - {request.title}",
                body=email_body,
            )
        )
