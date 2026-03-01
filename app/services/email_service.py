# app/services/email_service.py

import asyncio
import time

from app.common.request_state_config import REQUEST_STATE_CONFIG
from app.core.config import settings
from app.infrastructure.email.manager import EmailManager


class RequestEmailService:
    def __init__(self, email_manager: EmailManager):
        self.email_manager = email_manager

    def send_status_email(self, request, previous_status, new_status):
        config = REQUEST_STATE_CONFIG.get(previous_status, {}).get(new_status)
        if not config or not config.get("template"):
            return

        template_name = config["template"]
        template = self.email_manager.get_template(template_name)
        if not template:
            return

        notify_roles = config.get("notify_roles", [])
        recipients = []
        for role in notify_roles:
            attr = getattr(request, role.value.lower(), None)
            if attr and hasattr(attr, "email"):
                recipients.append(attr.email)

        if not recipients:
            return

        link = f"{settings.FRONTEND_URL}/requests/{request.id}"

        for recipient_email in recipients:
            email_body = template.substitute(
                request_code=f"REQ-{request.id}",
                request_title=request.title,
                user_name=f"{request.requester.first_name} {request.requester.last_name}",
                request_id=request.id,
                request_type=f"{request.type.name} > {request.subtype.name}",
                priority=request.priority.value,
                submitted_at=request.created_at.strftime("%B %d, %Y at %I:%M %p"),
                status=request.current_status.value,
                link=link,
            )

            subject_prefix = template_name.replace("REQUEST_", "").capitalize()

            time.sleep(10)

            asyncio.run(
                self.email_manager.send_email(
                    to=recipient_email,
                    subject=f"{subject_prefix} - REQ-{request.id} - {request.title}",
                    body=email_body,
                )
            )
