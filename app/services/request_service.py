# app/services/request_service.py
from typing import List

from fastapi import status

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

    def create_request(self, request_in):

        self._validate_type_and_subtype(request_in.type_id, request_in.subtype_id)
        return self.request_repo.create(request_in)

    def get_requests_by_user(self, user_id: int, statuses: List[str]):
        return self.request_repo.get_requests_by_user(user_id, statuses)
