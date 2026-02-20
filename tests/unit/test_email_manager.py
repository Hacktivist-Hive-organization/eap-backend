# tests/unit/test_email_manager.py

import pytest

from app.common.exceptions import ConfigurationException
from app.infrastructure.email.manager import EmailManager
from app.infrastructure.email.registry import EMAIL_PROVIDERS


class DummyProvider:
    async def send(self, to, subject, body, html=None):
        return None


def test_email_manager_invalid_provider(monkeypatch):
    monkeypatch.setattr(
        "app.infrastructure.email.manager.settings.EMAIL_SERVICE",
        "unknown",
    )

    with pytest.raises(ConfigurationException):
        EmailManager()


def test_email_manager_valid_provider(monkeypatch):
    monkeypatch.setitem(EMAIL_PROVIDERS, "dummy", DummyProvider)

    monkeypatch.setattr(
        "app.infrastructure.email.manager.settings.EMAIL_SERVICE",
        "dummy",
    )

    manager = EmailManager()
    assert manager is not None
