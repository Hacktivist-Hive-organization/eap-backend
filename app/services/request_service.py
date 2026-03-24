# app/services/request_service.py

from typing import List, Optional

from fastapi import BackgroundTasks, status

from app.common.enums import Status, UserRole
from app.common.exceptions import BusinessException
from app.common.request_workflow.request_transition_validator import (
    RequestTransitionValidator,
)
from app.common.security_models import CurrentUser
from app.core.config import settings
from app.infrastructure.email.templates import TEMPLATE_REGISTRY
from app.repositories import (
    RequestRepository,
    RequestSubtypeRepository,
    RequestTrackingRepository,
    RequestTypeApproverRepository,
    RequestTypeRepository,
    UserRepository,
)
from app.services.email_service import EmailService
from app.services.request_transitions.generic_handler import GenericStatusHandler
from app.services.request_transitions.in_progress_handler import InProgressHandler
from app.services.request_transitions.submitted_handler import SubmittedHandler


class RequestService:
    def __init__(
        self,
        request_repo: RequestRepository,
        type_repo: RequestTypeRepository,
        subtype_repo: RequestSubtypeRepository,
        email_service: EmailService,
        approver_repo: RequestTypeApproverRepository,
        tracking_repo: RequestTrackingRepository,
        user_repo: UserRepository,
    ):
        self.request_repo = request_repo
        self.type_repo = type_repo
        self.subtype_repo = subtype_repo
        self.user_repo = user_repo
        self.approver_repo = approver_repo
        self.tracking_repo = tracking_repo
        self.email_service = email_service
        self.transition_validator = RequestTransitionValidator(tracking_repo)

        # default generic handler for all statuses without a specific handler
        self.default_handler = GenericStatusHandler(
            request_repo=self.request_repo,
            tracking_repo=self.tracking_repo,
        )

        self.transition_handlers = {
            Status.SUBMITTED: SubmittedHandler(
                approver_repo=self.approver_repo,
                tracking_repo=self.tracking_repo,
                request_repo=self.request_repo,
            ),
            Status.IN_PROGRESS: InProgressHandler(
                tracking_repo=self.tracking_repo,
                request_repo=self.request_repo,
            ),
        }

    # ----------------------- PUBLIC METHODS -----------------------

    def create_request(self, request_in, current_user):
        current_user_id = current_user.id
        if current_user.role != UserRole.REQUESTER:
            raise BusinessException(
                message="Only requesters can create requests",
                status_code=status.HTTP_403_FORBIDDEN,
            )
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
                message="Not authorized to view this request",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return self.request_repo.get_requests_by_assignee_and_status(
            approver_id=current_user.id,
            statuses=statuses,
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
        comment: str | None = None,
        background_tasks: BackgroundTasks | None = None,
    ):
        request = self.request_repo.get_request_details(request_id)
        if not request:
            raise BusinessException(
                message="Request not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if comment and len(comment.strip()) < 5:
            raise BusinessException(
                message="Comment is mandatory and must be at least 5 characters long",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        rule = self.transition_validator.validate(
            request=request,
            new_status=status_in,
            user=current_user,
            comment=comment,
        )

        handler = self.transition_handlers.get(status_in, self.default_handler)

        try:
            result = handler.handle(
                request=request,
                user=current_user,
                comment=comment,
                new_status=status_in,
                rule=rule,
                background_tasks=background_tasks,
            )
        except BusinessException:
            raise
        except Exception:
            raise BusinessException(
                message="Internal server error",
                status_code=500,
            )

        if background_tasks and rule.get("notify_roles"):
            self._send_email_task(
                request=result,
                template_name=rule.get("template"),
                notify_roles=rule.get("notify_roles"),
                background_tasks=background_tasks,
            )

        return result

    def edit_draft_request(
        self, request_id: int, request_in, current_user: CurrentUser
    ):

        request = self.request_repo.get_request_details(request_id)
        if not request:
            raise BusinessException(
                message="Request not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if request.requester_id != current_user.id:
            raise BusinessException(
                message="Not authorized to submit this request",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        if request.current_status != Status.DRAFT:
            raise BusinessException(
                message="Only draft requests can be edited",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        # Convert input to dict, exclude unset
        update_data = request_in.model_dump(exclude_unset=True)

        # Business rule: status cannot be edited here
        if "current_status" in update_data:
            raise BusinessException(
                message="Updating request status is not allowed via this endpoint",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        # Validate type/subtype if they are provided
        type_id = update_data.get("type_id", request.type_id)
        subtype_id = update_data.get("subtype_id", request.subtype_id)
        self._validate_type_and_subtype(type_id, subtype_id)

        # Remove restricted fields
        restricted_fields = {"id", "requester_id", "created_at"}
        for field in restricted_fields:
            update_data.pop(field, None)

        try:
            updated_request = self.request_repo.update_request_fields(
                request, update_data
            )
        except Exception:
            raise BusinessException(
                message="Database error, Please contact your administrator",
                status_code=status.HTTP_417_EXPECTATION_FAILED,
            )

        # Re-fetch fully-loaded object to avoid detached relationships
        return self.request_repo.get_request_details(updated_request.id)

    def delete_draft_request(self, request_id: int, current_user: CurrentUser):
        """
        Deletes a draft request. Only the owner can delete, and only if it is in DRAFT status.
        """
        # Fetch the request to check ownership and status
        request = self.request_repo.get_request_details(request_id)
        if not request:
            raise BusinessException(
                message="Request not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if request.requester_id != current_user.id:
            raise BusinessException(
                message="You do not have permission to delete this request",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        if request.current_status != Status.DRAFT:
            raise BusinessException(
                message="Only draft requests can be deleted",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            self.request_repo.delete(request)

        except Exception:
            raise BusinessException(
                message="Database error while deleting request. Please contact your administrator",
                status_code=status.HTTP_417_EXPECTATION_FAILED,
            )

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
            pass
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

    def _send_email_task(self, request, template_name, notify_roles, background_tasks):

        template = TEMPLATE_REGISTRY.get(template_name)
        if not template:
            return

        recipients = set()

        for role in notify_roles:
            if role == UserRole.REQUESTER:
                recipients.add(request.requester.email)

            elif role == UserRole.ADMIN:
                admins = self.user_repo.get_by_role(UserRole.ADMIN)
                recipients.update([u.email for u in admins])

            elif role == UserRole.APPROVER:
                assignee = getattr(request, "assignee", None)
                if assignee:
                    recipients.add(assignee.email)

        for to in recipients:
            email_body = template.substitute(
                request_code=f"REQ-{request.id}",
                request_title=request.title,
                user_name=f"{request.requester.first_name} {request.requester.last_name}",
                request_id=request.id,
                request_type=f"{request.type.name} > {request.subtype.name}",
                priority=request.priority.value,
                submitted_at=request.created_at.strftime("%B %d, %Y at %I:%M %p"),
                status=request.current_status.value,
                link=f"{settings.FRONTEND_URL}/dashboard/all?requestId={request.id}",
            )

            subject_line = (
                f"{request.current_status.value} - REQ-{request.id} - {request.title}"
            )

            background_tasks.add_task(
                self.email_service.send_email,
                to=to,
                subject=subject_line,
                body=email_body,
            )
