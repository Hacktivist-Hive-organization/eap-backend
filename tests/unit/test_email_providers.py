# tests/unit/test_email_providers.py

import asyncio

from app.infrastructure.email.providers.dummy import DummyEmailService
from app.infrastructure.email.providers.mailjet import MailjetEmailService
from app.infrastructure.email.providers.mailtrap import MailtrapEmailService

TO = "test@example.com"
SUBJECT = "test_email_providers.py::test_provider_send"
BODY = "Body content for test_provider_send"
HTML = "<b>Body content for test_provider_send</b>"


def test_dummy_provider_send():
    provider = DummyEmailService()
    asyncio.run(provider.send(TO, SUBJECT, BODY, HTML))


# def test_mailtrap_provider_send():
#     provider = MailtrapEmailService()
#     asyncio.run(provider.send(TO, SUBJECT, BODY, HTML))


def test_mailjet_provider_send():
    provider = MailjetEmailService()
    asyncio.run(provider.send(TO, SUBJECT, BODY, HTML))
