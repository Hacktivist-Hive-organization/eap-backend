# app/infrastructure/email/providers/dummy_print.py

from pathlib import Path
from string import Template

from app.core.config import settings
from app.infrastructure.email.base import EmailService

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DUMMY_LOG_PATH = PROJECT_ROOT / "logs" / "dummy_email_log.txt"


class DummyPrintEmailService(EmailService):
    def __init__(self):
        self.enable_print = getattr(settings, "DUMMY_EMAIL_PRINT", True)

        DUMMY_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    async def send(
        self, to: str, subject: str, body: str, html: str | None = None
    ) -> None:
        if not self.enable_print:
            return

        print("=== DUMMY EMAIL ===")
        print(f"To: {to}")
        print(f"Subject: {subject}")
        print(f"Body:\n{body}")
        print("==================")

        with open(DUMMY_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(
                f"To: {to}\n" f"Subject: {subject}\n" f"Body:\n{body}\n" f"{'-'*50}\n"
            )

    @staticmethod
    def get_template(template_name: str) -> Template | None:
        return Template(f"{template_name} email for $user_name, request $request_id")
