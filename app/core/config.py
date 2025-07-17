"""
Centralised application settings loaded from environment variables.

Using Pydantic for robust parsing & validation.
"""

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load variables from a local .env file when running outside Docker
load_dotenv()


class Settings(BaseSettings):
    es_host: str = Field(..., env="ES_HOST")
    es_index: str = Field("documents", env="ES_INDEX")
    log_level: str = Field("INFO", env="LOG_LEVEL")

    class Config:
        case_sensitive = False


@lru_cache  # cached singleton
def get_settings() -> Settings:
    """
    Lazily load settings once and cache for future calls.
    """
    return Settings()  # reads env variables automatically
