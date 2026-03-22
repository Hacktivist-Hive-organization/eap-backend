# app/services/request_service.py

import asyncio
import time
from typing import List, Optional

from fastapi import BackgroundTasks, status
from sqlalchemy.exc import IntegrityError

from app.common.enums import Status, UserRole
from app.common.exceptions import BusinessException
from app.common.request_workflow.request_transition_validator import (
    RequestTransitionValidator,
)
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
        self.transition_validator = RequestTransitionValidator(tracking_repo)

    def create_request(self, request_in, current_user_id: int):
        self._validate_type_and_subtype(request_in.type_id, request_in.subtype_id)
        return self.request_repo.create(request_in, current_user_id)

    def get_all_requests(self):
        return self.request_repo.get_all_requests()

    def get_requests_by_statuses(self, statuses: List[Status]):
        if statuses:
            return self.request_repo.get_requests_by_statuses(statuses)
        return self.request_repo.get_all_requests()

    def get_requests_by_user(self, user_id: int, statuses: List[Status]):
        return self.request_repo.get_requests_by_user(user_id, statuses)

    def get_requests_for_approver(
        self, current_user, statuses: Optional[List[Status]] = None
    ) -> list:
        if current_user.role != UserRole.APPROVER:
            raise BusinessException(
                message="User is not an approver",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return self.request_repo.get_requests_by_assignee_and_status(
            approver_id=current_user.id, statuses=statuses
        )

    def get_request_details(self, request_id: int, current_user: CurrentUser):
        request = self.request_repo.get_request_details(request_id)
        if not request:
            raise BusinessException(
                message="Request not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        self._validate_view_permissions(request, current_user)
        return request

    def process_request(
        self,
        request_id: int,
        status_in: Status,
        current_user: CurrentUser,
        comment: Optional[str] = None,
        background_tasks: BackgroundTasks | None = None,
    ):
        request = self.request_repo.get_request_details(request_id)
        if not request:
            raise BusinessException(
                message="Request not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        rule = self.transition_validator.validate(
            request=request,
            new_status=status_in,
            user=current_user,
            comment=comment,
        )

        if status_in == Status.IN_PROGRESS:
            current_assignee = getattr(request, "assignee", None)

            if current_assignee:
                if current_assignee.id != current_user.id:
                    raise BusinessException(
                        message="Another admin already working on this request",
                        status_code=400,
                    )
                else:
                    raise BusinessException(
                        message="Request already assigned to you",
                        status_code=400,
                    )

            # Assign current admin as assignee
            request.assignee_id = current_user.id

        if status_in == Status.SUBMITTED:
            approver = self.approver_repo.get_least_busy(request.type_id)
            if not approver:
                raise BusinessException(
                    message="No approver configured for this request type",
                    status_code=status.HTTP_409_CONFLICT,
                )

            self.approver_repo.increment_workload(approver)

            try:
                request.current_status = Status.SUBMITTED
                self.request_repo.save(request)

                self.tracking_repo.create(
                    request_id=request.id,
                    user_id=approver.user_id,
                    status=Status.SUBMITTED,
                    comment="Request submitted and assigned to approver",
                    commit=False,
                )

                self.request_repo.db.commit()
                self.request_repo.db.refresh(request)

            except IntegrityError:
                self.request_repo.db.rollback()
                raise BusinessException(
                    message="Request cannot be submitted due to data conflict",
                    status_code=status.HTTP_409_CONFLICT,
                )
            except Exception:
                self.request_repo.db.rollback()
                raise BusinessException(
                    message="Internal server error",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return self.request_repo.get_request_details(request.id)

        updated_request = self._update_request_status(
            request, status_in, comment, current_user.id
        )
        self._send_email_if_required(updated_request, status_in, background_tasks)
        return updated_request

    # ----------------------- PRIVATE METHODS -----------------------

    def _validate_view_permissions(self, request, current_user: CurrentUser):
        if current_user.role == UserRole.REQUESTER:
            if request.requester_id != current_user.id:
                raise BusinessException(
                    message="You cannot view this request",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
        elif current_user.role == UserRole.APPROVER:
            tracking = self.tracking_repo.get_tracking_by_request_user_id(
                request.id, current_user.id
            )
            if not tracking:
                raise BusinessException(
                    message="You are not assigned to this request",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
        elif current_user.role == UserRole.ADMIN:
            pass  # Admin can view any request
        else:
            raise BusinessException(
                message="You cannot view this request",
                status_code=status.HTTP_403_FORBIDDEN,
            )

    def _validate_type_and_subtype(self, type_id: int, subtype_id: int):
        subtype = self.subtype_repo.get_by_id_and_type(subtype_id, type_id)
        if not subtype:
            raise BusinessException(
                message=f"Subtype {subtype_id} does not belong to type {type_id}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    def _update_request_status(
        self, request, status_in: Status, comment: Optional[str], user_id: int
    ):
        try:
            updated_req = self.request_repo.update_request_status(
                request, status_in, commit=False
            )
            self.tracking_repo.create(
                comment or f"Status changed to {status_in.value}",
                request.id,
                status_in,
                user_id,
                commit=False,
            )
            self.request_repo.db.commit()
            self.request_repo.db.refresh(updated_req)
            return updated_req
        except Exception:
            self.request_repo.db.rollback()
            raise BusinessException(
                message="Database error, Please contact your administrator",
                status_code=status.HTTP_417_EXPECTATION_FAILED,
            )

    def _send_email_if_required(
        self,
        request,
        status_in: Status,
        background_tasks: BackgroundTasks | None = None,
    ):
        if status_in not in [Status.APPROVED, Status.REJECTED] or not background_tasks:
            return
        background_tasks.add_task(self._send_email_task, request, status_in)

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
