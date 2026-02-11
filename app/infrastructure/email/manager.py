# app/infrastructure/email/manager.py

from app.core.config import settings
from app.infrastructure.email.registry import EMAIL_PROVIDERS


class EmailManager:
    def __init__(self):
        name = settings.EMAIL_SERVICE.lower()

        if name not in EMAIL_PROVIDERS:
            raise ValueError(f"Email provider '{name}' not registered")

        self._service = EMAIL_PROVIDERS[name]()

    async def send_email(
        self, to: str, subject: str, body: str, html: str | None = None
    ) -> None:
        await self._service.send(to, subject, body, html)
