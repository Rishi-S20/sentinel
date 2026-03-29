"""Price data poller — fetches OHLCV data for tracked assets.

This is the first worker to implement. It will:
1. Get the list of assets being tracked by any active agent
2. Fetch latest price data from Alpha Vantage / yfinance
3. Insert into the price_data TimescaleDB hypertable
"""

from app.workers.celery_app import celery_app
import logging
import asyncio
from sqlalchemy import select, distinct
from sqlalchemy.dialects.postgresql import insert
from app.database import async_session
from app.models.price_data import PriceData
from app.models.agent import Agent, agent_watchlist

import requests
from datetime import datetime, timezone
from app.config import settings


logger = logging.getLogger(__name__)


async def get_tracked_symbols() -> list[str]:
    """Get all unique asset symbols from active agent watchlists."""
    async with async_session() as session:
        result = await session.execute(
            select(distinct(agent_watchlist.c.asset_id))
            .join(Agent, Agent.id == agent_watchlist.c.agent_id)
            .where(Agent.status == "active")
        )
        return [row[0] for row in result.all()]


@celery_app.task(name="app.workers.price_poller.fetch_prices")
def fetch_prices():
    symbols = asyncio.run(get_tracked_symbols())
    total = 0
    for symbol in symbols:
        rows = fetch_ohlcv(symbol)
        save_prices(rows)
        total += len(rows)
        logger.info(f"Saved {len(rows)} rows for {symbol}")
    return {"status": "ok", "rows_saved": total}


def fetch_ohlcv(symbol: str) -> list[dict]:
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": settings.ALPHA_VANTAGE_API_KEY
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    time_series = data.get("Time Series (Daily)", {})

    rows = []
    for date_str, values in time_series.items():
        rows.append({
            "time": datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc),
            "asset_id": symbol,
            "open": float(values["1. open"]),
            "high": float(values["2. high"]),
            "low": float(values["3. low"]),
            "close": float(values["4. close"]),
            "volume": int(values["5. volume"]),
        })
    
    return rows


async def save_prices_async(rows: list[dict]):
    if not rows:
        return
    async with async_session() as session:
        stmt = insert(PriceData).values(rows).on_conflict_do_nothing()
        await session.execute(stmt)
        await session.commit()

def save_prices(rows: list[dict]):
    asyncio.run(save_prices_async(rows))
