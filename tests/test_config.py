# test_config.py

from unittest.mock import patch

class TestSettings:
    DATABASE_TYPE = "sqlite"
    DATABASE_HOST = "localhost"
    DATABASE_PORT = 5432
    DATABASE_USER = "user"
    DATABASE_PASSWORD = "pass"
    DATABASE_NAME = "test_db"
    JWT_SECRET_KEY = "secret"

def override_app_settings():
    with patch("app.core.config.settings") as mock_settings:
        mock_settings.DATABASE_TYPE = TestSettings.DATABASE_TYPE
        mock_settings.DATABASE_HOST = TestSettings.DATABASE_HOST
        mock_settings.DATABASE_PORT = TestSettings.DATABASE_PORT
        mock_settings.DATABASE_USER = TestSettings.DATABASE_USER
        mock_settings.DATABASE_PASSWORD = TestSettings.DATABASE_PASSWORD
        mock_settings.DATABASE_NAME = TestSettings.DATABASE_NAME
        mock_settings.JWT_SECRET_KEY = TestSettings.JWT_SECRET_KEY
        yield
