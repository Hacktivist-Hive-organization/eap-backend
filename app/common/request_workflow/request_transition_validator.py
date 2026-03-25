# app/common/request_workflow/request_transition_validator.py

from starlette import status

from app.common.enums import Status, UserRole
from app.common.exceptions import BusinessException
from app.common.request_workflow.request_state_config import REQUEST_STATE_CONFIG
from app.common.request_workflow.request_state_machine import RequestStateMachine


class RequestTransitionValidator:

    def __init__(self, tracking_repo):
        self.tracking_repo = tracking_repo

    def validate(self, request, new_status: Status, user, comment):
        current_status = request.current_status

        # 1. Check if role has any access to current status
        roles_allowed_any = {
            role
            for cfg in REQUEST_STATE_CONFIG.get(current_status, {}).values()
            for role in cfg["roles"]
        }
        if user.role not in roles_allowed_any:
            raise BusinessException(
                message="Role has no access to this request status",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        # 2. Check user-specific access
        if user.role == UserRole.APPROVER:
            tracking = self.tracking_repo.get_tracking_by_request_user_id(
                request.id, user.id
            )
            if not tracking:
                raise BusinessException(
                    message="Approver is not assigned to this request",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
        elif user.role == UserRole.REQUESTER and request.requester_id != user.id:
            raise BusinessException(
                message="You cannot view this request",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        # 3. Check role allowed for the specific transition
        transition_config = RequestStateMachine.get_rule(current_status, new_status)
        if not transition_config:
            raise BusinessException(
                message=f"Transition from {current_status.value} to {new_status.value} is invalid",
                status_code=status.HTTP_409_CONFLICT,
            )

        if user.role not in transition_config["roles"]:
            raise BusinessException(
                message=f"Role '{user.role.value}' is not allowed to perform transition "
                f"from {current_status.value} to {new_status.value}",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        # 4. Check comment requirement
        if transition_config.get("comment_required") and not comment:
            raise BusinessException(
                message="Comment is mandatory for this action",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        return transition_config
