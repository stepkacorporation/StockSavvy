import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

DEBUG: bool = os.getenv('DEBUG', 'False') == 'True'
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

if DEBUG:
    DOTENV = ROOT_DIR / 'docker/dev/.env'
else:
    DOTENV = ROOT_DIR / 'docker/prod/.env'


class Settings(BaseSettings):
    ALLOWED_HOSTS: list[str]

    SECRET_KEY: str

    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    # EMAIL_HOST: str
    # EMAIL_PORT: int
    # EMAIL_USE_TLS: bool
    # EMAIL_HOST_USER: str
    # EMAIL_HOST_PASSWORD: str
    # DEFAULT_FROM_EMAIL: str
    #
    # GOOGLE_CLIENT_ID: str
    # GOOGLE_SECRET: str
    #
    # YANDEX_CLIENT_ID: str
    # YANDEX_SECRET: str

    model_config = SettingsConfigDict(
        env_file=DOTENV,
        env_file_encoding='utf-8'
    )


settings = Settings()
