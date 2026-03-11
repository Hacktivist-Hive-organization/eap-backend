# tests/integration/email/test_email_service.py

import asyncio

import pytest

from app.core.config import settings
from app.infrastructure.email.manager import EmailManager
from app.services.email_service import EmailService


def test_service_full_cycle_from_env():
    provider_name = settings.EMAIL_SERVICE
    manager = EmailManager()
    service = EmailService(manager)

    to = "test@example.com"
    subject = (
        f"test_email_service.py::test_service_full_cycle_from_env::{provider_name}"
    )
    body = f"Body from test_email_service.py::test_service_full_cycle_from_env::{provider_name}"
    html = f"<b>Body from test_email_service.py::test_service_full_cycle_from_env::{provider_name}</b>"

    asyncio.run(service.send_email(to, subject, body, html))


def test_service_invalid_email():
    manager = EmailManager()
    service = EmailService(manager)

    with pytest.raises(ValueError):
        asyncio.run(
            service.send_email(
                "invalid-email",
                "subject",
                "body",
            )
        )


def test_service_empty_body():
    manager = EmailManager()
    service = EmailService(manager)

    with pytest.raises(ValueError):
        asyncio.run(
            service.send_email(
                "test@example.com",
                "subject",
                "",
            )
        )


def test_service_propagates_provider_exception():
    class FailingManager:
        async def send_email(self, *args, **kwargs):
            raise RuntimeError("provider failure")

    service = EmailService(FailingManager())

    with pytest.raises(RuntimeError):
        asyncio.run(
            service.send_email(
                "test@example.com",
                "test_email_service.py::test_service_propagates_provider_exception",
                "body",
            )
        )
