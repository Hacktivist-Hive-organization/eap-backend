# app/common/request_state_machine.py

from app.common.enums import Status, UserRole
from app.common.exceptions import BusinessException
from app.common.request_state_config import REQUEST_STATE_CONFIG


class RequestStateMachine:

    @classmethod
    def get_transition_config(cls, from_status: Status, to_status: Status):
        return REQUEST_STATE_CONFIG.get(from_status, {}).get(to_status)

    @classmethod
    def validate(
        cls, request, user_id: int, comment: str, request_tracking, status_in: Status
    ):
        from_status = request.current_status
        config = cls.get_transition_config(from_status, status_in)

        if config is None:
            raise BusinessException(
                message=f"Cannot transition from {from_status.value} to {status_in.value}",
                status_code=400,
            )

        roles = config.get("roles", [])
        if UserRole.ADMIN not in roles:
            is_requester = request.requester_id == user_id
            is_approver = bool(request_tracking)
            if UserRole.REQUESTER in roles and not is_requester:
                raise BusinessException(
                    message="You are not authorized to perform this action",
                    status_code=403,
                )
            if UserRole.APPROVER in roles and not is_approver:
                raise BusinessException(
                    message="You are not authorized to perform this action",
                    status_code=403,
                )

        if config.get("comment_required") and not comment:
            raise BusinessException(
                message=f"Comment is mandatory for this transition",
                status_code=400,
            )

        return config
