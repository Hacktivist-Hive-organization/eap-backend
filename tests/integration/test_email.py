# tests/integration/test_email.py

import asyncio
from unittest.mock import patch

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.api.dependencies.service_dependency import get_email_manager
from app.api.routes.v1.email_router import router as email_router
from app.common.exceptions import ConfigurationException, ExternalServiceException
from app.infrastructure.email.base import EmailService
from app.infrastructure.email.registry import EMAIL_PROVIDERS

# ------------------ Fixtures ------------------


@pytest.fixture(autouse=True)
def clear_email_manager_cache():
    get_email_manager.cache_clear()


@pytest.fixture
def app():
    app = FastAPI()
    app.include_router(email_router)

    # Override EmailManager dependency with a fake
    class FakeManager:
        async def send_email(self, to, subject, body, html=None):
            return None

    async def override_manager():
        return FakeManager()

    app.dependency_overrides[get_email_manager] = override_manager

    return app


# ------------------ Fake providers ------------------


class FakeEmailService(EmailService):
    async def send(self, to, subject, body, html=None):
        return None


class FailingEmailService(EmailService):
    async def send(self, to, subject, body, html=None):
        raise ExternalServiceException("failure")


# ------------------ EmailManager ------------------


def test_email_manager_init_success(monkeypatch):
    monkeypatch.setitem(EMAIL_PROVIDERS, "fake", FakeEmailService)
    monkeypatch.setattr(
        "app.infrastructure.email.manager.settings.EMAIL_SERVICE", "fake"
    )
    from app.infrastructure.email.manager import EmailManager

    manager = EmailManager()
    assert isinstance(manager._service, FakeEmailService)


def test_email_manager_invalid_provider(monkeypatch):
    monkeypatch.setattr(
        "app.infrastructure.email.manager.settings.EMAIL_SERVICE", "unknown"
    )
    import pytest

    from app.infrastructure.email.manager import EmailManager

    with pytest.raises(ConfigurationException):
        EmailManager()


def test_email_manager_send_calls_provider(monkeypatch):
    monkeypatch.setitem(EMAIL_PROVIDERS, "fake", FakeEmailService)
    monkeypatch.setattr(
        "app.infrastructure.email.manager.settings.EMAIL_SERVICE", "fake"
    )
    from app.infrastructure.email.manager import EmailManager

    manager = EmailManager()
    with patch.object(manager._service, "send", return_value=None) as mock_send:
        asyncio.run(manager.send_email("user@test.com", "Subj", "Body", "<b>html</b>"))
        mock_send.assert_called_once_with(
            "user@test.com", "Subj", "Body", "<b>html</b>"
        )


# ------------------ Endpoint success ------------------


def test_send_email_success(app):
    client = TestClient(app)
    response = client.post(
        "/send",
        json={"to": "user@example.com", "subject": "Test", "body": "Body"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "ok"


def test_send_email_with_html(app):
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


# ------------------ Endpoint failure ------------------


def test_send_email_provider_failure(app):
    # Override manager with failing provider
    class FailingManager:
        async def send_email(self, to, subject, body, html=None):
            raise ExternalServiceException("failure")

    async def override():
        return FailingManager()

    app.dependency_overrides[get_email_manager] = override
    client = TestClient(app, raise_server_exceptions=False)

    response = client.post(
        "/send",
        json={"to": "user@example.com", "subject": "Test", "body": "Body"},
    )
    assert response.status_code == 500


# ------------------ Validation ------------------


def test_send_email_invalid_email(app):
    client = TestClient(app)
    response = client.post(
        "/send",
        json={"to": "invalid-email", "subject": "Test", "body": "Body"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
