# tests/integration/test_email.py
import pytest
from fastapi.testclient import TestClient

from app.api.dependencies.service_dependency import get_email_manager
from app.common.exceptions import ExternalServiceException
from app.infrastructure.email.base import EmailService
from app.main import app


class DummyEmailService(EmailService):
    async def send(self, to, subject, body, html=None):
        return None


class FailingEmailService(EmailService):
    async def send(self, to, subject, body, html=None):
        raise ExternalServiceException("failure")


def _manager(service):
    class _M:
        async def send_email(self, to, subject, body, html=None):
            await service.send(to, subject, body, html)

    return _M()


@pytest.fixture
def client_with_success():
    app.dependency_overrides[get_email_manager] = lambda: _manager(DummyEmailService())
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def client_with_failure():
    app.dependency_overrides[get_email_manager] = lambda: _manager(
        FailingEmailService()
    )
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


BASE_URL = "/api/v1/email/send"


def test_send_email_success(client_with_success):
    response = client_with_success.post(
        BASE_URL, json={"to": "user@example.com", "subject": "Test", "body": "Body"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_send_email_with_html(client_with_success):
    response = client_with_success.post(
        BASE_URL,
        json={
            "to": "user@example.com",
            "subject": "Test",
            "body": "Body",
            "html": "<b>Hello</b>",
        },
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_send_email_invalid_email(client_with_success):
    response = client_with_success.post(
        BASE_URL, json={"to": "invalid-email", "subject": "Test", "body": "Body"}
    )
    assert response.status_code == 422


def test_send_email_provider_failure(client_with_failure):
    response = client_with_failure.post(
        BASE_URL, json={"to": "user@example.com", "subject": "Test", "body": "Body"}
    )
    assert response.status_code == 500
    assert response.json()["detail"] == "failure"
