"""SEC EDGAR crawler — downloads and parses 10-K, 10-Q, 8-K filings. Phase 2."""

from app.workers.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="app.workers.sec_crawler.crawl_filings")
def crawl_filings():
    logger.info("SEC crawler running — not yet implemented")
    return {"status": "not_implemented"}
