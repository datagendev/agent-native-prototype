"""Application configuration using Pydantic Settings."""

from enum import Enum
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvironmentType(str, Enum):
    """Application environment types."""

    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TEST = "test"


class Config(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    APP_NAME: str = "Webhook Service"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: EnvironmentType = EnvironmentType.DEVELOPMENT
    APP_SECRET_KEY: str = "change-me-in-production"
    APP_URL: str = "http://localhost:8000"
    PORT: int = 8000

    # Database (Neon Postgres)
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/webhook_service"
    SHOW_SQL_QUERIES: bool = False

    # Redis (Upstash)
    REDIS_URL: str = "redis://localhost:6379"

    # GitHub OAuth
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    GITHUB_REDIRECT_URI: str = "http://localhost:8000/auth/github/callback"

    # Cloudflare R2 (for repo storage)
    R2_ACCOUNT_ID: str = ""
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    R2_BUCKET_NAME: str = "webhook-service-repos"

    # Anthropic (for Claude agent execution)
    ANTHROPIC_API_KEY: str = ""

    # Rate Limits
    DEFAULT_RATE_LIMIT_PER_MINUTE: int = 10
    DEFAULT_RATE_LIMIT_PER_HOUR: int = 100
    USER_RATE_LIMIT_PER_MINUTE: int = 50
    USER_RATE_LIMIT_PER_HOUR: int = 500

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENVIRONMENT == EnvironmentType.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENVIRONMENT == EnvironmentType.PRODUCTION

    @property
    def is_test(self) -> bool:
        """Check if running in test mode."""
        return self.ENVIRONMENT == EnvironmentType.TEST


@lru_cache
def get_config() -> Config:
    """Get cached configuration instance."""
    return Config()


config = get_config()
