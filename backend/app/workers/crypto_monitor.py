"""Crypto monitor — fetches crypto prices and on-chain data. Phase 2."""

from app.workers.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="app.workers.crypto_monitor.fetch_crypto")
def fetch_crypto():
    logger.info("Crypto monitor running — not yet implemented")
    return {"status": "not_implemented"}
