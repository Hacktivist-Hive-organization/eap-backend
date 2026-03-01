# app/infrastructure/email/manager.py

from string import Template

from app.common.exceptions import ConfigurationException
from app.core.config import settings
from app.infrastructure.email.registry import EMAIL_PROVIDERS
from app.infrastructure.email.templates import TEMPLATE_REGISTRY


class EmailManager:
    def __init__(self):
        name = settings.EMAIL_SERVICE.lower()

        if name not in EMAIL_PROVIDERS:
            raise ConfigurationException(f"Email provider '{name}' not registered")

        self._service = EMAIL_PROVIDERS[name]()

    async def send_email(
        self, to: str, subject: str, body: str, html: str | None = None
    ) -> None:
        await self._service.send(to, subject, body, html)

    @staticmethod
    def get_template(template_name: str) -> Template | None:
        return TEMPLATE_REGISTRY.get(template_name)
