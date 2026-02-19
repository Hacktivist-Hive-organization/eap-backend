# tests/integration/test_email.py

import asyncio
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.api.dependencies.service_dependency import get_email_manager
from app.api.routes.v1.email_router import router as email_router
from app.common.exceptions import ConfigurationException, ExternalServiceException
from app.core.config import settings
from app.infrastructure.email.base import EmailService
from app.infrastructure.email.manager import EmailManager
from app.infrastructure.email.providers.mailjet import MailjetEmailService
from app.infrastructure.email.providers.mailtrap import MailtrapEmailService
from app.infrastructure.email.registry import EMAIL_PROVIDERS

# ---------- Fixtures ----------


@pytest.fixture(autouse=True)
def clear_email_manager_cache():
    get_email_manager.cache_clear()


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(email_router)
    return app


# ---------- Fake providers ----------


class FakeEmailService(EmailService):
    async def send(self, to, subject, body, html=None):
        return None


class FailingEmailService(EmailService):
    async def send(self, to, subject, body, html=None):
        raise ExternalServiceException("failure")


# ---------- EmailManager ----------


def test_email_manager_init_success(monkeypatch):
    monkeypatch.setitem(EMAIL_PROVIDERS, "fake", FakeEmailService)
    monkeypatch.setattr(
        "app.infrastructure.email.manager.settings.EMAIL_SERVICE", "fake"
    )

    manager = EmailManager()
    assert isinstance(manager._service, FakeEmailService)


def test_email_manager_invalid_provider(monkeypatch):
    monkeypatch.setattr(
        "app.infrastructure.email.manager.settings.EMAIL_SERVICE", "unknown"
    )

    with pytest.raises(ConfigurationException):
        EmailManager()


def test_email_manager_send_calls_provider(monkeypatch):
    monkeypatch.setitem(EMAIL_PROVIDERS, "fake", FakeEmailService)
    monkeypatch.setattr(
        "app.infrastructure.email.manager.settings.EMAIL_SERVICE", "fake"
    )

    manager = EmailManager()

    with patch.object(manager._service, "send", return_value=None) as mock_send:
        asyncio.run(manager.send_email("user@test.com", "Subj", "Body", "<b>html</b>"))

        mock_send.assert_called_once_with(
            "user@test.com", "Subj", "Body", "<b>html</b>"
        )


# ---------- Endpoint ----------


def test_send_email_success(app, monkeypatch):
    monkeypatch.setitem(EMAIL_PROVIDERS, "fake", FakeEmailService)
    monkeypatch.setattr(
        "app.infrastructure.email.manager.settings.EMAIL_SERVICE", "fake"
    )

    client = TestClient(app)

    response = client.post(
        "/send",
        json={
            "to": "user@example.com",
            "subject": "Test",
            "body": "Body",
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "ok"


def test_send_email_with_html(app, monkeypatch):
    monkeypatch.setitem(EMAIL_PROVIDERS, "fake", FakeEmailService)
    monkeypatch.setattr(
        "app.infrastructure.email.manager.settings.EMAIL_SERVICE", "fake"
    )

    client = TestClient(app)

    response = client.post(
        "/send",
        json={
            "to": "user@example.com",
            "subject": "Test",
            "body": "Body",
            "html": "<b>Hello</b>",
        },
    )

    assert response.status_code == status.HTTP_200_OK


def test_send_email_provider_failure(app, monkeypatch):
    monkeypatch.setitem(EMAIL_PROVIDERS, "fake", FailingEmailService)
    monkeypatch.setattr(
        "app.infrastructure.email.manager.settings.EMAIL_SERVICE", "fake"
    )

    client = TestClient(app, raise_server_exceptions=False)

    response = client.post(
        "/send",
        json={
            "to": "user@example.com",
            "subject": "Test",
            "body": "Body",
        },
    )

    assert response.status_code == 500


def test_send_email_invalid_email(app):
    client = TestClient(app)

    response = client.post(
        "/send",
        json={
            "to": "invalid-email",
            "subject": "Test",
            "body": "Body",
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# ---------- Mailjet ----------


def test_mailjet_missing_credentials(monkeypatch):
    monkeypatch.setattr(settings, "MAILJET_API_KEY", None)
    monkeypatch.setattr(settings, "MAILJET_SECRET_KEY", None)

    with pytest.raises(ConfigurationException):
        MailjetEmailService()


def test_mailjet_send_success(monkeypatch):
    monkeypatch.setattr(settings, "MAILJET_API_KEY", "key")
    monkeypatch.setattr(settings, "MAILJET_SECRET_KEY", "secret")
    monkeypatch.setattr(settings, "MAIL_FROM_EMAIL", "from@test.com")
    monkeypatch.setattr(settings, "MAIL_FROM_NAME", "Test")

    with patch("app.infrastructure.email.providers.mailjet.Client") as mock_client:
        instance = mock_client.return_value
        instance.send.create.return_value.status_code = 200
        instance.send.create.return_value.text = "ok"

        service = MailjetEmailService()
        asyncio.run(service.send("to@test.com", "Subj", "Body"))


def test_mailjet_send_failure(monkeypatch):
    monkeypatch.setattr(settings, "MAILJET_API_KEY", "key")
    monkeypatch.setattr(settings, "MAILJET_SECRET_KEY", "secret")
    monkeypatch.setattr(settings, "MAIL_FROM_EMAIL", "from@test.com")
    monkeypatch.setattr(settings, "MAIL_FROM_NAME", "Test")

    with patch("app.infrastructure.email.providers.mailjet.Client") as mock_client:
        instance = mock_client.return_value
        instance.send.create.return_value.status_code = 500
        instance.send.create.return_value.text = "error"

        service = MailjetEmailService()

        with pytest.raises(ExternalServiceException):
            asyncio.run(service.send("to@test.com", "Subj", "Body"))


# ---------- Mailtrap ----------


def test_mailtrap_missing_credentials(monkeypatch):
    monkeypatch.setattr(settings, "MAILTRAP_USER", None)
    monkeypatch.setattr(settings, "MAILTRAP_SMTP_PASSWORD", None)

    with pytest.raises(ConfigurationException):
        MailtrapEmailService()


def test_mailtrap_send_success(monkeypatch):
    monkeypatch.setattr(settings, "MAILTRAP_USER", "user")
    monkeypatch.setattr(settings, "MAILTRAP_SMTP_PASSWORD", "pass")
    monkeypatch.setattr(settings, "MAILTRAP_SMTP_HOST", "smtp.test")
    monkeypatch.setattr(settings, "MAILTRAP_SMTP_PORT", 587)
    monkeypatch.setattr(settings, "MAIL_FROM_EMAIL", "from@test.com")
    monkeypatch.setattr(settings, "MAIL_FROM_NAME", "Test")

    with patch("smtplib.SMTP") as mock_smtp:
        service = MailtrapEmailService()
        asyncio.run(service.send("to@test.com", "Subj", "Body"))

        assert mock_smtp.called
