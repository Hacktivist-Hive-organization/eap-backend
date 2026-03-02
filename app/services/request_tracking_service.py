# app/services/request_tracking_service.py

from typing import List

from fastapi import BackgroundTasks
from starlette import status

from app.common.enums import Status, UserRole
from app.common.exceptions import BusinessException
from app.common.request_state_machine import RequestStateMachine
from app.infrastructure.email.manager import EmailManager
from app.repositories import RequestRepository, RequestTrackingRepository
from app.services.email_service import RequestEmailService


class RequestTrackingService:

    def __init__(
        self,
        repo: RequestTrackingRepository,
        request_repo: RequestRepository,
        email_manager: EmailManager,
    ):
        self.repo = repo
        self.request_repo = request_repo
        self.email_service = RequestEmailService(email_manager)

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
        comment: str = "",
        background_tasks: BackgroundTasks | None = None,
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
        config = RequestStateMachine.validate(
            request, user_id, comment, request_tracking, status_in
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

        if background_tasks and config.get("template"):
            background_tasks.add_task(
                self.email_service.send_status_email,
                request,
                request.current_status,
                status_in,
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
        self, current_user, statuses: List[Status] | None = None
    ) -> list:
        if current_user.role != UserRole.APPROVER:
            raise BusinessException(
                message="User is not an approver",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        return self.repo.get_requests_for_approver(
            approver_id=current_user.id, statuses=statuses
        )
