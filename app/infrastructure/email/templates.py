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
