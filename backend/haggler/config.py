"""Application config loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All app config in one place. Read once at startup."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM
    anthropic_api_key: str = Field(..., description="Anthropic API key for negotiator")
    anthropic_model: str = "claude-sonnet-4-6"

    # Database
    database_url: str = "sqlite+aiosqlite:///./haggler.db"

    # Apify (Craigslist + Facebook scouts)
    apify_api_key: str | None = None

    # eBay
    ebay_app_id: str | None = None
    ebay_cert_id: str | None = None
    ebay_sandbox: bool = True

    # Email relay (Craigslist)
    gmail_user: str | None = None
    gmail_app_password: str | None = None
    imap_host: str = "imap.gmail.com"
    smtp_host: str = "smtp.gmail.com"

    # Logging
    log_level: str = "INFO"

    # Negotiation knobs
    max_concurrent_negotiations: int = 8
    negotiation_timeout_hours: int = 24
    good_enough_discount: float = Field(
        default=0.30,
        description="Stop searching when we hit this discount off asking",
    )


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
