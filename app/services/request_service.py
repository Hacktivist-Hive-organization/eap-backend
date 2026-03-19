# app/services/request_service.py

import asyncio
import time
from typing import List, Optional

from fastapi import BackgroundTasks, status

from app.common.enums import Status, UserRole
from app.common.exceptions import BusinessException
from app.common.security_models import CurrentUser
from app.core.config import settings
from app.infrastructure.email.templates import REQUEST_APPROVED, REQUEST_REJECTED
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

    def get_request_details(self, request_id: int, current_user: CurrentUser):
        request = self.request_repo.get_request_details(request_id)
        if not request:
            raise BusinessException(
                message="Request not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        self._validate_view_permissions(request, current_user)
        return request

    def _validate_view_permissions(self, request, current_user: CurrentUser):
        # Request owner
        if request.requester_id == current_user.id:
            return

        # Admin restriction
        if current_user.role == UserRole.ADMIN:
            if request.current_status == Status.DRAFT:
                raise BusinessException(
                    message="Request is still in draft state",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
            else:
                return

        # Assigned users
        tracking = self.tracking_repo.get_tracking_by_request_user_id(
            request.id, current_user.id
        )

        if not tracking:
            raise BusinessException(
                message="Not authorized to view this request",
                status_code=status.HTTP_403_FORBIDDEN,
            )

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

    def process_request(
        self,
        request_id: int,
        status_in: Status,
        current_user: CurrentUser,
        comment: str,
        background_tasks: BackgroundTasks | None = None,
    ):
        if current_user.role == UserRole.ADMIN:
            return self._admin_process_request(
                request_id, status_in, current_user, comment, background_tasks
            )
        else:
            return self._process_request(
                request_id, status_in, current_user.id, comment, background_tasks
            )

    def _process_request(
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
        request_tracking = self.tracking_repo.get_tracking_by_request_user_id(
            request_id, user_id
        )

        if status_in == Status.CANCELLED:
            # Requester (owner) can cancel
            if user_id != request.requester_id:
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

        if status_in not in [Status.APPROVED, Status.REJECTED, Status.CANCELLED]:
            raise BusinessException(
                message="Invalid status transition",
                status_code=status.HTTP_400_BAD_REQUEST,
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

        try:
            updated_req = self.request_repo.update_request_status(
                request, status_in, commit=False
            )
            self.tracking_repo.create(
                comment, request_id, status_in, user_id, commit=False
            )

            self.request_repo.db.commit()
            self.request_repo.db.refresh(updated_req)
        except Exception:
            self.request_repo.db.rollback()
            raise BusinessException(
                message="Database error, Please contact your administrator",
                status_code=status.HTTP_417_EXPECTATION_FAILED,
            )

        if status_in in [Status.REJECTED, Status.APPROVED] and background_tasks:
            background_tasks.add_task(self._send_email_task, request, status_in)

        return request

    def _admin_process_request(
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

        if request.current_status in [
            Status.REJECTED,
            Status.COMPLETED,
            Status.CANCELLED,
        ]:
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
                request, status_in, commit=False
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

    def _send_email_task(self, request, status_in: Status):
        requester = request.requester
        link = f"{settings.FRONTEND_URL}/dashboard/all?requestId={request.id}"
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

        return self.request_repo.get_requests_by_assignee_and_status(
            approver_id=current_user.id, statuses=statuses
        )

    def reopen_request(self, request_id: int, user_id: int):
        request = self.request_repo.get_request_details(request_id)
        if not request:
            raise BusinessException(
                message="Request not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        if request.requester_id != user_id:
            raise BusinessException(
                message="You do not have permission to perform this action",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        if request.current_status != Status.CANCELLED:
            raise BusinessException(
                message=f"you can not reopen {request.current_status} requests",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        updated_request = self.request_repo.update_request_status(
            request, Status.DRAFT, commit=False
        )

        try:
            self.tracking_repo.create(
                "reopen cancelled request",
                request_id,
                Status.DRAFT,
                user_id,
                commit=False,
            )

            self.tracking_repo.db.commit()
            self.request_repo.db.refresh(updated_request)
        except Exception:
            self.request_repo.db.rollback()
            raise BusinessException(
                message="Database error, Please contact your administrator",
                status_code=status.HTTP_417_EXPECTATION_FAILED,
            )

        return updated_request
