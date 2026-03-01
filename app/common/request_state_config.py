# app/common/request_state_config.py

from app.common.enums import Status, UserRole

REQUEST_STATE_CONFIG = {
    (Status.DRAFT, Status.SUBMITTED): {
        "roles": [UserRole.REQUESTER],
        "comment_required": False,
        "notify_roles": [UserRole.APPROVER],
        "template": "REQUEST_SUBMITTED",
    },
    (Status.SUBMITTED, Status.APPROVED): {
        "roles": [UserRole.APPROVER],
        "comment_required": False,
        "notify_roles": [UserRole.REQUESTER],
        "template": "REQUEST_APPROVED",
    },
    (Status.SUBMITTED, Status.REJECTED): {
        "roles": [UserRole.APPROVER],
        "comment_required": True,
        "notify_roles": [UserRole.REQUESTER],
        "template": "REQUEST_REJECTED",
    },
    (Status.SUBMITTED, Status.CANCELLED): {
        "roles": [UserRole.REQUESTER],
        "comment_required": False,
        "notify_roles": [],
        "template": None,
    },
}
