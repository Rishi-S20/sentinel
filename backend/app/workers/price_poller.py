"""Price data poller — fetches OHLCV data for tracked assets.

This is the first worker to implement. It will:
1. Get the list of assets being tracked by any active agent
2. Fetch latest price data from Alpha Vantage / yfinance
3. Insert into the price_data TimescaleDB hypertable
"""

from app.workers.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="app.workers.price_poller.fetch_prices")
def fetch_prices():
    """Fetch latest price data for all tracked assets."""
    # TODO: Implement in Phase 2
    # 1. Query DB for all unique assets in active agent watchlists
    # 2. For each asset, fetch OHLCV from yfinance
    # 3. Upsert into price_data table
    logger.info("Price poller running — not yet implemented")
    return {"status": "not_implemented"}
