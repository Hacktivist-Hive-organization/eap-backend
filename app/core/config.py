import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.core.static_conf import *

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),  # Automatically uses .env.test if ENV_FILE set
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    APP_NAME: str = APP_NAME
    APP_VERSION: str = APP_VERSION
    API_V1_PREFIX: str = API_V1_PREFIX

    # DATABASE
    DATABASE_TYPE: str
    DATABASE_HOST: str | None = None
    DATABASE_PORT: int | None = None
    DATABASE_USER: str | None = None
    DATABASE_PASSWORD: str | None = None
    DATABASE_NAME: str
    DATABASE_ECHO: bool = False

    # JWT
    JWT_SECRET_KEY: str

    # CORS
    CORS_ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]
    MIDDLEWARE_CORS: bool = True

def get_settings() -> Settings:
    return Settings()

settings = get_settings()
