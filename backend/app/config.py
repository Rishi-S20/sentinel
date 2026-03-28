from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ---- App ----
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: str = '["http://localhost:5173"]'

    # ---- Database ----
    DATABASE_URL: str = "postgresql+asyncpg://sentinel:sentinel_dev_password@db:5432/sentinel"
    DATABASE_URL_SYNC: str = "postgresql://sentinel:sentinel_dev_password@db:5432/sentinel"

    # ---- Redis ----
    REDIS_URL: str = "redis://redis:6379/0"

    # ---- Auth ----
    STACK_PROJECT_ID: str = ""
    STACK_SECRET_SERVER_KEY: str = ""

    # ---- AI / LLM ----
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # ---- Market Data ----
    ALPHA_VANTAGE_API_KEY: str = ""

    # ---- News ----
    NEWS_API_KEY: str = ""

    # ---- Reddit ----
    REDDIT_CLIENT_ID: str = ""
    REDDIT_CLIENT_SECRET: str = ""
    REDDIT_USER_AGENT: str = "sentinel-bot/0.1"

    # ---- Stripe ----
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # ---- Email ----
    SENDGRID_API_KEY: str = ""
    FROM_EMAIL: str = "briefings@sentinel.app"

    @property
    def cors_origins_list(self) -> List[str]:
        return json.loads(self.CORS_ORIGINS)

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
