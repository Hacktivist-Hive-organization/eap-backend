# tests/integration/email/test_email_manager.py

import asyncio

import pytest

import app.core.config as config
from app.common.exceptions import ConfigurationException
from app.infrastructure.email.manager import EmailManager
from app.infrastructure.email.registry import EMAIL_PROVIDERS

# @pytest.mark.parametrize("provider_name", list(EMAIL_PROVIDERS.keys()))
# def test_manager_delegates_to_all_providers(monkeypatch, provider_name):
#     monkeypatch.setattr(config.settings, "EMAIL_SERVICE", provider_name)
#     manager = EmailManager()
#     to = "test@example.com"
#     subject = f"test_email_manager.py::test_manager_delegates_to_all_providers {provider_name}"
#     body = f"Body content for test_email_manager.py::test_manager_delegates_to_all_providers using {provider_name}"
#     html = f"<b>Body content for test_email_manager.py::test_manager_delegates_to_all_providers using {provider_name}</b>"
#
#     asyncio.run(manager.send_email(to, subject, body, html))


def test_manager_invalid_provider(monkeypatch):
    monkeypatch.setattr(config.settings, "EMAIL_SERVICE", "nonexistent_provider")
    with pytest.raises(ConfigurationException):
        EmailManager()


def test_manager_from_env():
    provider_name = config.settings.EMAIL_SERVICE
    manager = EmailManager()
    to = "test@example.com"
    subject = f"test_email_manager.py::test_manager_from_env {provider_name}"
    body = f"Body content for test_email_manager.py::test_manager_from_env using {provider_name}"
    html = f"<b>Body content for test_email_manager.py::test_manager_from_env using {provider_name}</b>"

    asyncio.run(manager.send_email(to, subject, body, html))
