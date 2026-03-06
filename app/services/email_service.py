# app/services/email_service.py

import re
from typing import Protocol


class EmailManagerProtocol(Protocol):
    async def send_email(
        self, to: str, subject: str, body: str, html: str | None = None
    ) -> None: ...


class EmailService:
    EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    def __init__(self, manager: EmailManagerProtocol):
        if manager is None:
            raise ValueError("EmailManager is required")
        self._manager = manager

    async def send_email(
        self, to: str, subject: str, body: str, html: str | None = None
    ) -> None:
        if not to or not self.EMAIL_REGEX.match(to):
            raise ValueError("Invalid email address")

        if not body or not body.strip():
            raise ValueError("Email body cannot be empty")

        await self._manager.send_email(
            to=to,
            subject=subject,
            body=body,
            html=html,
        )
