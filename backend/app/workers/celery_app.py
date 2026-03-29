"""Celery application configuration."""

from celery import Celery
from celery.schedules import crontab
import os

# Use sync Redis URL for Celery broker
redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "sentinel",
    broker=redis_url,
    backend=redis_url,
)

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Timezone
    timezone="UTC",
    enable_utc=True,

    # Task discovery — auto-find tasks in worker modules
    imports=[
        "app.workers.price_poller",
        "app.workers.news_fetcher",
        "app.workers.sec_crawler",
        "app.workers.social_scraper",
        "app.workers.crypto_monitor",
        "app.workers.embedding_pipeline",
        "app.workers.agent_runner",
    ],

    # Periodic task schedule (Celery Beat)
    beat_schedule={
        # ---- Data Ingestion ----
        "poll-stock-prices": {
            "task": "app.workers.price_poller.fetch_prices",
            "schedule": 300.0,  # Every 5 minutes
        },
        # These will be uncommented as we build each worker:
        "fetch-news": {
            "task": "app.workers.news_fetcher.fetch_news",
            "schedule": 900.0,  # Every 15 minutes
        },
        # "crawl-sec-filings": {
        #     "task": "app.workers.sec_crawler.crawl_filings",
        #     "schedule": crontab(hour="*/6"),  # Every 6 hours
        # },
        # "scrape-social": {
        #     "task": "app.workers.social_scraper.scrape_sentiment",
        #     "schedule": 1800.0,  # Every 30 minutes
        # },
        # "poll-crypto-prices": {
        #     "task": "app.workers.crypto_monitor.fetch_crypto",
        #     "schedule": 600.0,  # Every 10 minutes
        # },

        # ---- Agent Runs ----
        "run-agents": {
            "task": "app.workers.agent_runner.run_due_agents",
            "schedule": 3600.0,  # Every hour
        },
    },
)
