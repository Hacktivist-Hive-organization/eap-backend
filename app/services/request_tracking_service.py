from typing import List, Optional

from starlette import status

from app.common.enums import Status, UserRole
from app.common.exceptions import BusinessException
from app.repositories import RequestRepository, RequestTrackingRepository


class RequestTrackingService:

    def __init__(
        self, repo: RequestTrackingRepository, request_repo: RequestRepository
    ):
        self.repo = repo
        self.request_repo = request_repo

    def get_request_tracking_by_request_id(self, request_id: int, user_id: int):
        if not self.request_repo.is_request_owned_by_user(request_id, user_id):
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
    ):
        request = self.request_repo.get_request_details(request_id)

        # check if the request exists
        if not request:
            raise BusinessException(
                message="Request not found", status_code=status.HTTP_404_NOT_FOUND
            )

        # check if the request is already assigned to the user
        request_tracking = self.repo.get_tracking_by_request_user_id(
            request_id, user_id
        )
        if not request_tracking:
            raise BusinessException(
                message="You are not authorized to process this request",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        # check if request status = submitted
        if (
            request.current_status != Status.SUBMITTED
            or request_tracking.status != Status.SUBMITTED
        ):
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
