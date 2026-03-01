# app/infrastructure/email/providers/dummy.py

from string import Template

from app.core.config import settings
from app.infrastructure.email.base import EmailService


class DummyEmailService(EmailService):
    def __init__(self):
        self.enable_print = getattr(settings, "DUMMY_EMAIL_PRINT", True)

    async def send(
        self, to: str, subject: str, body: str, html: str | None = None
    ) -> None:
        pass

    @staticmethod
    def get_template(template_name: str) -> Template | None:
        return Template(f"{template_name} email for $user_name, request $request_id")
