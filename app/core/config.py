import os

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.static_conf import *


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE_PATH", ".env"),  # Default to .env,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    APP_NAME: str = APP_NAME
    APP_VERSION: str = APP_VERSION
    API_V1_PREFIX: str = API_V1_PREFIX

    # Environment & Logging
    APP_ENV: str = "development"  # development | production
    LOG_LEVEL: str = "INFO"  # DEBUG | INFO | WARNING | ERROR

    # DATABASE
    DATABASE_TYPE: str
    DATABASE_HOST: str | None = None
    DATABASE_PORT: int | None = None
    DATABASE_USER: str | None = None
    DATABASE_PASSWORD: str | None = None
    DATABASE_NAME: str | None = None
    DATABASE_SCHEMA: str | None = None
    DATABASE_ECHO: bool = False

    # JWT
    JWT_SECRET_KEY: str

    # CORS
    CORS_ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite server
    ]
    MIDDLEWARE_CORS: bool = True
    DEVELOPMENT_ENVIRONMENT: bool = False

    # Email
    EMAIL_SERVICE: str = "mailtrap"

    # Sender
    MAIL_FROM_EMAIL: str | None = None
    MAIL_FROM_NAME: str | None = None

    # Mailtrap
    MAILTRAP_USER: str | None = None
    MAILTRAP_SMTP_PASSWORD: str | None = None

    MAILTRAP_SMTP_HOST: str | None = None
    MAILTRAP_SMTP_PORT: int = 587
    MAILTRAP_USE_TLS: bool = True

    # Mailjet
    MAILJET_API_KEY: str | None = None
    MAILJET_SECRET_KEY: str | None = None


def get_settings() -> Settings:
    return Settings()


settings = get_settings()
