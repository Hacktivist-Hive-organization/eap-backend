# app/services/request_transitions/in_progress_handler.py

from starlette import status

from app.common.enums import Status
from app.common.exceptions import BusinessException


class InProgressHandler:
    def __init__(self, tracking_repo, request_repo):
        self.tracking_repo = tracking_repo
        self.request_repo = request_repo

    def handle(
        self,
        request,
        user,
        comment,
        new_status=None,
        rule=None,
        background_tasks=None,
    ):
        current_assignee = getattr(request, "assignee", None)

        if request.current_status == Status.IN_PROGRESS:
            if current_assignee:
                if current_assignee.id == user.id:
                    raise BusinessException(
                        message="Request already assigned to you",
                        status_code=status.HTTP_409_CONFLICT,
                    )
                else:
                    raise BusinessException(
                        message="Another admin already working on this request",
                        status_code=status.HTTP_409_CONFLICT,
                    )

        if request.current_status == Status.APPROVED:
            request.assignee_id = user.id

        try:
            updated_req = self.request_repo.update_request_status(
                request, new_status, commit=False
            )

            self.tracking_repo.create(
                comment or f"Status changed to {new_status.value}",
                request.id,
                new_status,
                user.id,
                commit=False,
            )

            self.request_repo.db.commit()
            self.request_repo.db.refresh(updated_req)

            return updated_req

        except Exception:
            self.request_repo.db.rollback()
            raise BusinessException(
                message="Database error, Please contact your administrator",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
