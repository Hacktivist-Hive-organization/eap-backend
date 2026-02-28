# app/common/request_state_config.py

# app/common/request_state_config.py
from app.common.enums import Status

# key = (from_status, to_status)
# roles
# comment_required
# notify_roles
# template = (templates.py)

REQUEST_STATE_CONFIG = {
    (Status.DRAFT, Status.SUBMITTED): {
        "roles": ["requester"],
        "comment_required": False,
        "notify_roles": ["approver"],
        "template": "REQUEST_SUBMITTED",
    },
    (Status.SUBMITTED, Status.APPROVED): {
        "roles": ["approver"],
        "comment_required": False,
        "notify_roles": ["requester"],
        "template": "REQUEST_APPROVED",
    },
    (Status.SUBMITTED, Status.REJECTED): {
        "roles": ["approver"],
        "comment_required": True,
        "notify_roles": ["requester"],
        "template": "REQUEST_REJECTED",
    },
    (Status.SUBMITTED, Status.CANCELLED): {
        "roles": ["requester", "approver"],
        "comment_required": False,
        "notify_roles": [],
        "template": None,
    },
}
