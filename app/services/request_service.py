# app/services/request_service.py

from typing import List

from fastapi import status

from app.common.enums import Status
from app.common.exceptions import BusinessException
from app.infrastructure.email.manager import EmailManager
from app.infrastructure.email.templates import REQUEST_SUBMITTED
from app.repositories import (
    RequestRepository,
    RequestSubtypeRepository,
    RequestTrackingRepository,
    RequestTypeApproverRepository,
    RequestTypeRepository,
)


class RequestService:

    def __init__(
        self,
        request_repo: RequestRepository,
        type_repo: RequestTypeRepository,
        subtype_repo: RequestSubtypeRepository,
        email_manager: EmailManager,
        approver_repo: RequestTypeApproverRepository,
        tracking_repo: RequestTrackingRepository,
    ):
        self.request_repo = request_repo
        self.type_repo = type_repo
        self.subtype_repo = subtype_repo
        self.approver_repo = approver_repo
        self.tracking_repo = tracking_repo
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

    def submit_existing_request(
        self,
        request_id: int,
        current_user_id: int,
    ):
        request = self.request_repo.get_request_details(request_id)

        if not request:
            raise BusinessException(
                message="Request not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if request.requester_id != current_user_id:
            raise BusinessException(
                message="Not authorized to submit this request",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        if request.current_status != Status.DRAFT:
            raise BusinessException(
                message="Only draft requests can be submitted",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        #  Get default approver
        approver = self.approver_repo.get_default_or_available(request.type_id)

        if not approver:
            raise BusinessException(
                message="No approver configured for this request type",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        #  Change ONLY status
        request.current_status = Status.SUBMITTED

        self.request_repo.save(request)
        self.approver_repo.increment_workload(approver)

        #  Create tracking entry (store approver here)
        self.tracking_repo.create(
            request_id=request.id,
            user_id=approver.user_id,
            status=Status.SUBMITTED,
            comment="Request submitted and assigned to approver",
        )

        return request
