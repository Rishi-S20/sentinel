"""Social sentiment scraper — monitors Reddit for asset mentions. Phase 2."""

from app.workers.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="app.workers.social_scraper.scrape_sentiment")
def scrape_sentiment():
    logger.info("Social scraper running — not yet implemented")
    return {"status": "not_implemented"}
