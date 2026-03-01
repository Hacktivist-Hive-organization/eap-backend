# app/infrastructure/email/templates.py

from string import Template

REQUEST_SUBMITTED = Template(
    """Subject: Request Submitted - $request_code - $request_title

Dear $user_name,

Your request has been successfully submitted.

Request Details:

Request ID: $request_id
Title: $request_title
Type: $request_type
Priority: $priority
Submitted: $submitted_at
Status: $status

View Request Details: $link

Best regards,
EAP System
"""
)

REQUEST_REJECTED = Template(
    """Subject: Request Rejected - $request_code - $request_title

Dear $user_name,

Your request has been rejected.

Request Details:

Request ID: $request_id
Title: $request_title
Type: $request_type
Priority: $priority
Submitted: $submitted_at
Status: $status

View Request Details: $link

Best regards,
EAP System
"""
)

REQUEST_APPROVED = Template(
    """Subject: Request Approved - $request_code - $request_title

Dear $user_name,

Your request has been approved.

Request Details:

Request ID: $request_id
Title: $request_title
Type: $request_type
Priority: $priority
Submitted: $submitted_at
Status: $status

View Request Details: $link

Best regards,
EAP System
"""
)

TEMPLATE_REGISTRY = {
    "REQUEST_SUBMITTED": REQUEST_SUBMITTED,
    "REQUEST_REJECTED": REQUEST_REJECTED,
    "REQUEST_APPROVED": REQUEST_APPROVED,
}
