from starlette import status

from app.common.exceptions import BusinessException
from app.repositories import RequestTrackingRepository, RequestRepository


class RequestTrackingService:

    def __init__(self, repo: RequestTrackingRepository, request_repo:RequestRepository):
        self.repo = repo
        self.request_repo = request_repo

    def get_request_tracking_by_request_id(self, request_id: int, user_id: int):
        if not self.request_repo.is_request_owned_by_user(request_id, user_id):
            raise BusinessException(
                message="You do not have permission to track this request",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return (self.repo.get_request_tracking_by_request_id(request_id))
