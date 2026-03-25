# app/infrastructure/email/templates.py

from string import Template

REQUEST_DRAFT = Template(
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
Desk-X System
"""
)

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
Desk-X System
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
Desk-X System
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
Desk-X System
"""
)

REQUEST_CANCELLED = Template(
    """Subject: Request Cancelled - $request_code - $request_title

Dear $user_name,

Your request has been cancelled.

Request Details:

Request ID: $request_id
Title: $request_title
Type: $request_type
Priority: $priority
Submitted: $submitted_at
Status: $status

View Request Details: $link

Best regards,
Desk-X System
"""
)

REQUEST_IN_PROGRESS = Template(
    """Subject: Request In Progress - $request_code - $request_title

Dear $user_name,

Your request is now in progress.

Request Details:

Request ID: $request_id
Title: $request_title
Type: $request_type
Priority: $priority
Submitted: $submitted_at
Status: $status

View Request Details: $link

Best regards,
Desk-X System
"""
)

REQUEST_COMPLETED = Template(
    """Subject: Request Completed - $request_code - $request_title

Dear $user_name,

Your request has been completed.

Request Details:

Request ID: $request_id
Title: $request_title
Type: $request_type
Priority: $priority
Submitted: $submitted_at
Status: $status

View Request Details: $link

Best regards,
Desk-X System
"""
)

TEMPLATE_REGISTRY = {
    "REQUEST_DRAFT": REQUEST_DRAFT,
    "REQUEST_SUBMITTED": REQUEST_SUBMITTED,
    "REQUEST_APPROVED": REQUEST_APPROVED,
    "REQUEST_REJECTED": REQUEST_REJECTED,
    "REQUEST_CANCELLED": REQUEST_CANCELLED,
    "REQUEST_IN_PROGRESS": REQUEST_IN_PROGRESS,
    "REQUEST_COMPLETED": REQUEST_COMPLETED,
}
