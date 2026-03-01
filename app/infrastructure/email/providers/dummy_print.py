# app/infrastructure/email/providers/dummy_print.py

from string import Template

from app.core.config import settings
from app.infrastructure.email.base import EmailService


class DummyPrintEmailService(EmailService):
    def __init__(self):
        self.enable_print = getattr(settings, "DUMMY_EMAIL_PRINT", True)

    async def send(
        self, to: str, subject: str, body: str, html: str | None = None
    ) -> None:
        if self.enable_print:
            print("=== DUMMY EMAIL ===")
            print(f"To: {to}")
            print(f"Subject: {subject}")
            print(f"Body:\n{body}")
            print("==================")

            with open("dummy_email_log.txt", "a", encoding="utf-8") as f:
                f.write(f"To: {to}\nSubject: {subject}\nBody:\n{body}\n{'-'*50}\n")

    @staticmethod
    def get_template(template_name: str) -> Template | None:
        return Template(f"{template_name} email for $user_name, request $request_id")
