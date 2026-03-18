# app/common/request_workflow/request_transition_validator.py

from starlette import status

from app.common.enums import UserRole
from app.common.exceptions import BusinessException
from app.common.request_workflow.request_state_machine import RequestStateMachine


class RequestTransitionValidator:

    def __init__(self, repo):
        self.repo = repo

    def validate(self, request, next_status, user_id, comment):
        rule = RequestStateMachine.get_rule(request.current_status, next_status)

        if not rule:
            raise BusinessException(
                message=f"Request cannot be {next_status.value} because it is in {request.current_status.value} status",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        user = request.requester if request.requester_id == user_id else None
        if not user:
            user = next(
                (t.user for t in request.req_tracking if t.user_id == user_id), None
            )

        if not user:
            raise BusinessException(
                message="User not related to this request",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        if user.role not in rule["roles"]:
            raise BusinessException(
                message="You are not authorized to process this request",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        if rule["comment_required"] and not comment:
            raise BusinessException(
                message="Comment is mandatory for rejection",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return rule
