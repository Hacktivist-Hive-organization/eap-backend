# app/services/request_tracking_service.py

from starlette import status

from app.common.enums import UserRole
from app.common.exceptions import BusinessException
from app.common.security_models import CurrentUser
from app.repositories import RequestRepository, RequestTrackingRepository


class RequestTrackingService:

    def __init__(
        self,
        repo: RequestTrackingRepository,
        request_repo: RequestRepository,
    ):
        self.repo = repo
        self.request_repo = request_repo

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
