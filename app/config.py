from dotenv import load_dotenv
import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
# DB_ENV_FILE = os.getenv("DB_ENV_FILE", ".db.env")


class DataBaseSettings(BaseSettings):
    """Конфиги базы данных."""

    model_config = SettingsConfigDict(case_sensitive=False, env_prefix='POSTGRES_', env_file=BASE_DIR / ".db.env")
    host: str
    port: str
    db: str
    user: str
    password: str
    test_db: str


class AppSettings(BaseSettings):
    """Конфиги приложения."""

    model_config = SettingsConfigDict(case_sensitive=False, env_file=BASE_DIR / ".env",)

    debug: bool
    crypt_context_schema: str
    crypt_context_deprecated: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    test_base_url: str


db_settings = DataBaseSettings()
app_settings = AppSettings()