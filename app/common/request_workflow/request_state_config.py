# app/common/request_workflow/request_state_config.py

from app.common.enums import Status, UserRole

REQUEST_STATE_CONFIG = {
    Status.DRAFT: {
        Status.SUBMITTED: {
            "roles": [UserRole.REQUESTER],
            "comment_required": False,
            "template": "REQUEST_SUBMITTED",
            "notify_roles": [UserRole.APPROVER],
        },
    },
    Status.SUBMITTED: {
        Status.CANCELLED: {
            "roles": [UserRole.REQUESTER],
            "comment_required": False,
            "template": "REQUEST_CANCELLED",
            "notify_roles": [UserRole.APPROVER],
        },
        Status.APPROVED: {
            "roles": [UserRole.APPROVER],
            "comment_required": False,
            "template": "REQUEST_APPROVED",
            "notify_roles": [UserRole.ADMIN],
        },
        Status.REJECTED: {
            "roles": [UserRole.APPROVER],
            "comment_required": True,
            "template": "REQUEST_REJECTED",
            "notify_roles": [UserRole.REQUESTER],
        },
    },
    Status.APPROVED: {
        Status.IN_PROGRESS: {
            "roles": [UserRole.ADMIN],
            "comment_required": False,
            "template": "REQUEST_IN_PROGRESS",
            "notify_roles": [],
        }
    },
    Status.IN_PROGRESS: {
        Status.COMPLETED: {
            "roles": [UserRole.ADMIN],
            "comment_required": False,
            "template": "REQUEST_COMPLETED",
            "notify_roles": [],
        },
        Status.REJECTED: {
            "roles": [UserRole.ADMIN],
            "comment_required": False,
            "template": "REQUEST_REJECTED",
            "notify_roles": [],
        },
    },
}
