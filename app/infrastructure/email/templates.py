# app/infrastructure/email/templates.py

from string import Template

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
