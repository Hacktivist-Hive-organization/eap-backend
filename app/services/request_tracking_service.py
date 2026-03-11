# app/services/request_tracking_service.py

import asyncio
import time
from typing import List, Optional

from fastapi import BackgroundTasks
from starlette import status

from app.common.enums import Status, UserRole
from app.common.exceptions import BusinessException
from app.core.config import settings
from app.infrastructure.email.templates import REQUEST_APPROVED, REQUEST_REJECTED
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
        comment: str,
        background_tasks: BackgroundTasks | None = None,
    ):
        request = self.request_repo.get_request_details(request_id)

        # check if the request exists
        if not request:
            raise BusinessException(
                message="Request not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # check if the request is already assigned to the user
        request_tracking = self.repo.get_tracking_by_request_user_id(
            request_id, user_id
        )

        if status_in == Status.CANCELLED:
            # Requester (owner) or assigned approver can cancel
            if user_id != request.requester_id and not request_tracking:
                raise BusinessException(
                    message="You are not authorized to cancel this request",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
        else:
            # Only the assigned approver can approve or reject
            if not request_tracking:
                raise BusinessException(
                    message="You are not authorized to process this request",
                    status_code=status.HTTP_403_FORBIDDEN,
                )

        # check if request status = submitted
        if request.current_status != Status.SUBMITTED:
            raise BusinessException(
                message=f"Request cannot be {status_in.value} because it is in {request.current_status.value} status",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # for reject request, comment must be mandatory
        if status_in == Status.REJECTED and not comment:
            raise BusinessException(
                message="Comment is mandatory for rejection",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if status_in not in [Status.APPROVED, Status.REJECTED, Status.CANCELLED]:
            raise BusinessException(
                message="Invalid status transition",
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

        if status_in in [Status.REJECTED, Status.APPROVED] and background_tasks:
            background_tasks.add_task(self._send_email_task, request, status_in)

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
        """
        Returns requests assigned to the current approver, optionally filtered by statuses.
        """
        if current_user.role != UserRole.APPROVER:
            raise BusinessException(
                message="User is not an approver",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        return self.repo.get_requests_for_approver(
            approver_id=current_user.id, statuses=statuses
        )

    def _send_email_task(self, request, status_in: Status):
        requester = request.requester
        link = f"{settings.FRONTEND_URL}/requests/{request.id}"
        template = (
            REQUEST_REJECTED if status_in == Status.REJECTED else REQUEST_APPROVED
        )

        email_body = template.substitute(
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

        subject_prefix = (
            "Request Rejected" if status_in == Status.REJECTED else "Request Approved"
        )

        time.sleep(10)

        asyncio.run(
            self.email_service.send_email(
                to=requester.email,
                subject=f"{subject_prefix} - REQ-{request.id} - {request.title}",
                body=email_body,
            )
        )
