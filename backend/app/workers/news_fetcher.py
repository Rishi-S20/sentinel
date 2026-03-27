"""News fetcher — pulls articles from NewsAPI and Finnhub. Phase 2."""

from app.workers.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="app.workers.news_fetcher.fetch_news")
def fetch_news():
    logger.info("News fetcher running — not yet implemented")
    return {"status": "not_implemented"}
