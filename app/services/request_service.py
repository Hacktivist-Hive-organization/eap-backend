# app/services/request_service.py

from typing import List

from fastapi import status

from app.common.enums import Status
from app.common.exceptions import BusinessException
from app.repositories import (
    RequestRepository,
    RequestSubtypeRepository,
    RequestTypeRepository,
)


class RequestService:

    def __init__(
        self,
        request_repo: RequestRepository,
        type_repo: RequestTypeRepository,
        subtype_repo: RequestSubtypeRepository,
    ):
        self.request_repo = request_repo
        self.type_repo = type_repo
        self.subtype_repo = subtype_repo

    def _validate_type_and_subtype(self, type_id: int, subtype_id: int):
        """
        Private helper to validate:
        1. Type exists
        2. Subtype belongs to type
        Raises BusinessException if invalid.
        """
        if not self.type_repo.get_by_id(type_id):
            raise BusinessException(
                message=f"Request type not found: no type exists with id {type_id}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if not self.subtype_repo.get_by_id_and_type(subtype_id, type_id):
            raise BusinessException(
                message=f"Request subtype mismatch: no subtype with id {subtype_id} belongs to type {type_id}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    def create_request(self, request_in, current_user_id: int):

        self._validate_type_and_subtype(request_in.type_id, request_in.subtype_id)
        return self.request_repo.create(request_in, current_user_id)

    def get_requests_by_user(self, user_id: int, statuses: List[Status]):
        requests = self.request_repo.get_requests_by_user(user_id, statuses)
        if len(requests) == 0:
            raise BusinessException(
                message="No requests founded",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return self.request_repo.get_requests_by_user(user_id, statuses)

    def get_request_details(self, request_id: int, user_id: int):
        request = self.request_repo.get_request_details(request_id)

        if not request:
            raise BusinessException(
                message="Request not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if request.requester_id != user_id:
            raise BusinessException(
                message="Not authorized to view this request",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        return request
