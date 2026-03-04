# tests/unit/test_email_providers.py

import asyncio

import pytest

from app.infrastructure.email.providers.dummy import DummyEmailService
from app.infrastructure.email.providers.mailjet import MailjetEmailService
from app.infrastructure.email.providers.mailtrap import MailtrapEmailService


@pytest.mark.parametrize(
    "provider_class", [DummyEmailService, MailtrapEmailService, MailjetEmailService]
)
def test_provider_send(provider_class):
    provider = provider_class()
    to = "test@example.com"
    subject = "test_email_providers.py::test_provider_send"
    body = "Body content for test_provider_send"
    html = "<b>Body content for test_provider_send</b>"

    asyncio.run(provider.send(to, subject, body, html))
