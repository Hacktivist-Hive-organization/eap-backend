# app/services/email_service.py

import re
from typing import Protocol

from fastapi import BackgroundTasks

from app.core.config import settings


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

    def send_verification_email(
        self,
        to: str,
        token: str,
        background_tasks: BackgroundTasks,
    ):
        link = f"{settings.FRONTEND_URL}/verify-email#{token}"
        subject = "Email verification"
        body = f"Use the following link to verify your email: {link}"
        background_tasks.add_task(
            self.send_email,
            to=to,
            subject=subject,
            body=body,
        )

    def send_account_verified_email(
        self,
        to: str,
        background_tasks: BackgroundTasks,
    ):
        subject = "Account verified"
        body = "Your account has been successfully verified."
        background_tasks.add_task(
            self.send_email,
            to=to,
            subject=subject,
            body=body,
        )

    def send_password_reset_email(
        self,
        to: str,
        token: str,
        background_tasks: BackgroundTasks,
    ):
        link = f"{settings.FRONTEND_URL}/reset-password#{token}"
        subject = "Password reset"
        body = f"Use the following link to reset your password: {link}"
        background_tasks.add_task(
            self.send_email,
            to=to,
            subject=subject,
            body=body,
        )
