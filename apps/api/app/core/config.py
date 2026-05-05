"""Application settings and typed environment configuration."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed settings model for the AEO API."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="AEO Report Card API", alias="APP_NAME")
    app_env: Literal["development", "staging", "production"] = Field(
        default="development", alias="APP_ENV"
    )
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    database_url: str = Field(default="sqlite+pysqlite:///./aeo_local.db", alias="DATABASE_URL")

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4.1-mini", alias="OPENAI_MODEL")

    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-5-haiku-latest", alias="ANTHROPIC_MODEL")

    gemini_api_key: str | None = Field(default=None, alias="GEMINI_API_KEY")
    gemini_model: str = Field(default="gemini-2.0-flash", alias="GEMINI_MODEL")

    serpapi_key: str | None = Field(default=None, alias="SERPAPI_KEY")
    http_timeout_seconds: int = Field(default=25, alias="HTTP_TIMEOUT_SECONDS")

    @model_validator(mode="after")
    def normalize_database_url(self) -> "Settings":
        """Normalize Railway/Postgres URLs to psycopg SQLAlchemy driver format."""
        if self.database_url.startswith("postgres://"):
            self.database_url = self.database_url.replace("postgres://", "postgresql+psycopg://", 1)
        elif self.database_url.startswith("postgresql://") and "+psycopg" not in self.database_url:
            self.database_url = self.database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return singleton application settings."""
    return Settings()
