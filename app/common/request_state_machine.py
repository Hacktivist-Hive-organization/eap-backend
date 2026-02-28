# app/common/request_state_machine.py
from app.common.enums import Status


class RequestStateMachine:

    TRANSITIONS = {
        Status.DRAFT: [Status.SUBMITTED],
        Status.SUBMITTED: [Status.APPROVED, Status.REJECTED, Status.CANCELLED],
        Status.APPROVED: [],
        Status.REJECTED: [],
        Status.CANCELLED: [],
    }

    EMAIL_TEMPLATES = {
        Status.SUBMITTED: {
            "template": "REQUEST_SUBMITTED",
            "notify_roles": ["approver"],
        },
        Status.APPROVED: {
            "template": "REQUEST_APPROVED",
            "notify_roles": ["requester"],
        },
        Status.REJECTED: {
            "template": "REQUEST_REJECTED",
            "notify_roles": ["requester"],
        },
    }

    @classmethod
    def allowed_next_statuses(cls, current_status: Status):
        return cls.TRANSITIONS.get(current_status, [])

    @classmethod
    def get_transition_config(cls, next_status: Status):
        return cls.EMAIL_TEMPLATES.get(next_status, {})

    @classmethod
    def validate(cls, request, user_id, comment, request_tracking, status_in: Status):
        allowed = cls.allowed_next_statuses(request.current_status)
        if status_in not in allowed:
            raise ValueError(
                f"Invalid status transition from {request.current_status} to {status_in}"
            )
        return cls.get_transition_config(status_in)
