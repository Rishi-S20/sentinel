"""Price data poller — fetches OHLCV data for tracked assets via Finnhub."""

from app.workers.celery_app import celery_app
import logging
from sqlalchemy import select, distinct
from sqlalchemy.dialects.postgresql import insert
from app.database import sync_session
from app.models.price_data import PriceData
from app.models.agent import Agent, agent_watchlist

import finnhub
from datetime import datetime, timezone
from app.config import settings

logger = logging.getLogger(__name__)

finnhub_client = finnhub.Client(api_key=settings.FINNHUB_API_KEY)


def get_tracked_symbols() -> list[str]:
    with sync_session() as session:
        result = session.execute(
            select(distinct(agent_watchlist.c.asset_id))
            .join(Agent, Agent.id == agent_watchlist.c.agent_id)
            .where(Agent.status == "active")
        )
        return [row[0] for row in result.all()]


@celery_app.task(name="app.workers.price_poller.fetch_prices")
def fetch_prices():
    symbols = get_tracked_symbols()
    total = 0
    for symbol in symbols:
        rows = fetch_ohlcv(symbol)
        if rows:
            save_prices(rows)
            total += len(rows)
            logger.info(f"Saved {len(rows)} rows for {symbol}")
    return {"status": "ok", "rows_saved": total}


def fetch_ohlcv(symbol: str) -> list[dict]:
    try:
        quote = finnhub_client.quote(symbol)
    except Exception as e:
        logger.warning(f"Finnhub error for {symbol}: {e}")
        return []

    if not quote.get("c"):
        logger.warning(f"No quote data for {symbol}")
        return []

    return [{
        "time": datetime.now(timezone.utc),
        "asset_id": symbol,
        "open": quote["o"],
        "high": quote["h"],
        "low": quote["l"],
        "close": quote["c"],
        "volume": 0,
    }]



def save_prices(rows: list[dict]):
    with sync_session() as session:
        stmt = insert(PriceData).values(rows).on_conflict_do_nothing()
        session.execute(stmt)
        session.commit()
