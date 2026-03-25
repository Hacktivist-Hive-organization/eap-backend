# app/services/request_transitions/submitted_handler.py

from sqlalchemy.exc import IntegrityError
from starlette import status

from app.common.enums import Status
from app.common.exceptions import BusinessException


class SubmittedHandler:

    def __init__(self, approver_repo, tracking_repo, request_repo, email_service=None):
        self.approver_repo = approver_repo
        self.tracking_repo = tracking_repo
        self.request_repo = request_repo
        self.email_service = email_service

    def handle(
        self,
        request,
        user,
        comment,
        new_status=None,
        rule=None,
        background_tasks=None,
    ):
        assignee = getattr(request, "assignee", None)
        if new_status in [Status.APPROVED, Status.REJECTED]:
            if not assignee or assignee.user_id != user.id:
                raise BusinessException(
                    message="You are not assigned to approve this request",
                    status_code=status.HTTP_403_FORBIDDEN,
                )

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

            if (
                self.email_service
                and background_tasks
                and rule
                and rule.get("notify_roles")
            ):
                background_tasks.add_task(
                    self.email_service.send_email,
                    to=approver.email,
                    subject=f"New request assigned - REQ-{request.id}",
                    body=f"You have a new request assigned: {request.title}",
                )

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
