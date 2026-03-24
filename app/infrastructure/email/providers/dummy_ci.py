# app/infrastructure/email/providers/dummy_ci.py

from app.infrastructure.email.base import EmailService


class DummyCIEmailService(EmailService):
    async def send(
        self, to: str, subject: str, body: str, html: str | None = None
    ) -> None:
        return
