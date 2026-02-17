# app/services/request_service.py

from typing import List

from fastapi import status

from app.common.enums import Status
from app.common.exceptions import BusinessException
from app.infrastructure.email.templates import REQUEST_SUBMITTED
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
        email_manager,
    ):
        self.request_repo = request_repo
        self.type_repo = type_repo
        self.subtype_repo = subtype_repo
        self.email_manager = email_manager

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
        request = self.request_repo.create(request_in, current_user_id)

        email_body = REQUEST_SUBMITTED.substitute(
            request_code=f"REQ-{request.id}",
            user_name=request.user.full_name,
            request_id=request.id,
            request_title=request.title,
            request_type=f"{request.type.name} > {request.subtype.name}",
            priority=request.priority,
            submitted_at=request.created_at.strftime("%B %d, %Y at %I:%M %p"),
            status=request.status.value,
            link=f"https://your-system.com/requests/{request.id}",
        )

        self.email_manager.send_email(
            to=request.user.email,
            subject=f"Request Submitted - REQ-{request.id} - {request.title}",
            body=email_body,
        )

        return request

    def get_requests_by_user(self, user_id: int, statuses: List[Status]):
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
