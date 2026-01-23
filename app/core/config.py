# config.py

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.static_conf import *


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    APP_NAME: str = APP_NAME
    APP_VERSION: str = APP_VERSION
    API_V1_PREFIX: str = API_V1_PREFIX

    # .env
    DATABASE_TYPE = "postgresql"
    DATABASE_HOST = "127.0.0.1"
    DATABASE_PORT = 5432
    DATABASE_USER = "user1"
    DATABASE_PASSWORD = "user123"
    DATABASE_NAME = "Motopp"

    JWT_SECRET_KEY = "G7v!fR2xQ9zL#pW6mS0kT8dJ3hU1yN4bV5aC2eM9qR7tY8wX0zP6jH4uL1oK3i"

    # DATABASE
    DATABASE_TYPE: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    DATABASE_ECHO: bool = False

    # JWT
    JWT_SECRET_KEY: str

    # CORS
    CORS_ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite server
    ]
    MIDDLEWARE_CORS: bool = True


def get_settings() -> Settings:
    return Settings()  # noinspection PyArgumentList


settings = get_settings()
