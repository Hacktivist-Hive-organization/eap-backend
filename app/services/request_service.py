# app/services/request_service.py

from typing import List, Optional

from fastapi import BackgroundTasks, status
from sqlalchemy.orm import Session

from app.common.enums import Status, UserRole
from app.common.exceptions import BusinessException
from app.common.security_models import CurrentUser
from app.repositories import (
    RequestRepository,
    RequestSubtypeRepository,
    RequestTrackingRepository,
    RequestTypeApproverRepository,
    RequestTypeRepository,
)
from app.services.email_service import EmailService


class RequestService:

    def __init__(
        self,
        request_repo: RequestRepository,
        type_repo: RequestTypeRepository,
        subtype_repo: RequestSubtypeRepository,
        email_service: EmailService,
        approver_repo: RequestTypeApproverRepository,
        tracking_repo: RequestTrackingRepository,
    ):
        self.request_repo = request_repo
        self.type_repo = type_repo
        self.subtype_repo = subtype_repo
        self.approver_repo = approver_repo
        self.tracking_repo = tracking_repo
        self.email_service = email_service

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

    def get_all_requests(self):
        return self.request_repo.get_all_requests()

    def get_requests_by_statuses(self, statuses: List[Status]):
        if statuses:
            return self.request_repo.get_requests_by_statuses(statuses)
        return self.request_repo.get_all_requests()

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
        approver = self.approver_repo.get_least_busy(request.type_id)

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

        # expire_on_commit=False keeps req_tracking stale; expire it so the
        # next selectinload query picks up the newly committed tracking entry
        self.request_repo.db.expire(request, ["req_tracking"])
        return self.request_repo.get_request_details(request.id)

    def create_and_submit_request(self, request_in, current_user_id: int):
        self._validate_type_and_subtype(request_in.type_id, request_in.subtype_id)
        #  Get lowest-workload approver
        approver = self.approver_repo.get_least_busy(request_in.type_id)
        if not approver:
            raise BusinessException(
                message="No approver configured for this request type",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        request = self.request_repo.create(
            request_in, current_user_id, Status.SUBMITTED
        )
        # Increment approver workload
        self.approver_repo.increment_workload(approver)
        #  Create tracking entry (store approver here)
        self.tracking_repo.create(
            request_id=request.id,
            user_id=approver.user_id,
            status=Status.SUBMITTED,
            comment="Request submitted and assigned to approver",
        )
        return request

    def admin_process_request(
        self,
        request_id: int,
        status_in: Status,
        user: CurrentUser,
        comment: Optional[str] = None,
        background_tasks: BackgroundTasks | None = None,
    ):
        if user.role != UserRole.ADMIN:
            raise BusinessException(
                message="You do not have permission to perform this action",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        allowed_status = {Status.IN_PROGRESS, Status.COMPLETED, Status.REJECTED}

        if status_in not in allowed_status:
            raise BusinessException(
                message="Invalid status transition, Status should be "
                "in_progress, completed or rejected",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        request = self.request_repo.get_request_details(request_id)
        # check if the request exists
        if not request:
            raise BusinessException(
                message="Request not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if request.current_status in [Status.DRAFT, Status.SUBMITTED]:
            raise BusinessException(
                message="Request must be approved first",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if request.current_status in [Status.REJECTED, Status.COMPLETED]:
            raise BusinessException(
                message=f"Request already {request.current_status.value}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if (
            request.assignee
            and request.assignee.role == UserRole.ADMIN
            and request.assignee.id != user.id
        ):
            raise BusinessException(
                message="Another admin already working on this request",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        elif (
            request.current_status == Status.IN_PROGRESS
            and status_in == Status.IN_PROGRESS
        ):
            raise BusinessException(
                message="Invalid status transition, You are already assigned to this request.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # for reject request, comment must be mandatory
        if (
            status_in in [Status.COMPLETED, Status.REJECTED]
            and request.current_status != Status.IN_PROGRESS
        ):
            raise BusinessException(
                message="Please Assign the request to yourself first",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        if status_in == Status.REJECTED and not comment:
            raise BusinessException(
                message="Comment is mandatory for rejection",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        db = self.request_repo.db
        try:
            updated_request = self.request_repo.update_request_status(
                request, status_in
            )

            # create tracking record (this determines the assignee)
            self.tracking_repo.create(
                comment, request_id, status_in, user.id, commit=False
            )
            self.tracking_repo.db.commit()
            db.refresh(updated_request)
        except Exception:
            self.tracking_repo.db.rollback()
            raise BusinessException(
                message="Database error, Please contact your administrator",
                status_code=status.HTTP_417_EXPECTATION_FAILED,
            )

        return updated_request
