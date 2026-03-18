# app/common/request_workflow/request_state_config.py

from app.common.enums import Status, UserRole

REQUEST_STATE_CONFIG = {
    Status.DRAFT: {
        Status.SUBMITTED: {
            "roles": [UserRole.REQUESTER],
            "comment_required": False,
            "notify_roles": [UserRole.REQUESTER, UserRole.APPROVER],
            "template": "REQUEST_SUBMITTED",
        },
    },
    Status.SUBMITTED: {
        Status.CANCELLED: {
            "roles": [UserRole.REQUESTER],
            "comment_required": False,
            "notify_roles": [UserRole.REQUESTER, UserRole.APPROVER],
            "template": "REQUEST_CANCELLED",
        },
        Status.APPROVED: {
            "roles": [UserRole.APPROVER],
            "comment_required": False,
            "notify_roles": [UserRole.REQUESTER, UserRole.ADMIN],
            "template": "REQUEST_APPROVED",
        },
        Status.REJECTED: {
            "roles": [UserRole.APPROVER],
            "comment_required": True,
            "notify_roles": [UserRole.REQUESTER],
            "template": "REQUEST_REJECTED",
        },
    },
    Status.APPROVED: {
        Status.IN_PROGRESS: {
            "roles": [UserRole.ADMIN],
            "comment_required": False,
            "notify_roles": [UserRole.REQUESTER],
            "template": "REQUEST_IN_PROGRESS",
        }
    },
    Status.IN_PROGRESS: {
        Status.COMPLETED: {
            "roles": [UserRole.ADMIN],
            "comment_required": False,
            "notify_roles": [UserRole.REQUESTER],
            "template": "REQUEST_COMPLETED",
        },
        Status.REJECTED: {
            "roles": [UserRole.ADMIN],
            "comment_required": False,
            "notify_roles": [UserRole.REQUESTER],
            "template": "REQUEST_REJECTED",
        },
    },
}
