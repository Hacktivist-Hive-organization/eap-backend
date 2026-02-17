# app/services/email_service.py

from app.infrastructure.email.manager import EmailManager


class EmailService:
    def __init__(self, manager: EmailManager):
        self._manager = manager

    async def send_test_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: str | None = None,
    ) -> None:
        await self._manager.send_email(
            to=to,
            subject=subject,
            body=body,
            html=html,
        )
