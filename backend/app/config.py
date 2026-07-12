"""Application configuration.

APP_NAME and APP_TAGLINE are the single source of truth for branding.
Changing the product name later should be a one-line edit here.
"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

APP_NAME = "PulseMSME AI"
APP_TAGLINE = "MSME Financial Health Card for Bank Relationship Managers"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = APP_NAME
    app_tagline: str = APP_TAGLINE

    gemini_api_key: str = ""
    groq_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    groq_model: str = "llama-3.1-8b-instant"
    preferred_llm_provider: str = "gemini"

    llm_timeout_seconds: float = 12.0

    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
