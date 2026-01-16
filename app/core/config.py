from pydantic_settings import BaseSettings, SettingsConfigDict
from app.core.static_conf import *

class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding='utf-8',
        extra='ignore',
        case_sensitive=True,
    )

    APP_NAME: str = APP_NAME
    APP_VERSION: str = APP_VERSION
    API_V1_PREFIX: str = API_V1_PREFIX

    # DATABASE
    DATABASE_TYPE: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_SCHEMA: str
    DATABASE_ECHO: bool = False


    # CORS
    CORS_ALLOWED_ORIGINS: list[str] = [
        'http://localhost:3000',  # React dev server
        'http://localhost:5173' # Vite server
    ]
    MIDDLEWARE_CORS: bool = True

def get_settings() -> Settings:
    return Settings()

settings = get_settings()
