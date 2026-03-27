"""Price data poller — fetches OHLCV data for tracked assets.

This is the first worker to implement. It will:
1. Get the list of assets being tracked by any active agent
2. Fetch latest price data from Alpha Vantage / yfinance
3. Insert into the price_data TimescaleDB hypertable
"""

from app.workers.celery_app import celery_app
import logging
import yfinance as yf
import asyncio
from sqlalchemy.dialects.postgresql import insert
from app.database import async_session
from app.models.price_data import PriceData


logger = logging.getLogger(__name__)


@celery_app.task(name="app.workers.price_poller.fetch_prices")
def fetch_prices():
    """Fetch latest price data for all tracked assets."""
    # TODO: Implement in Phase 2
    # 1. Query DB for all unique assets in active agent watchlists
    # 2. For each asset, fetch OHLCV from yfinance
    # 3. Upsert into price_data table

    rows=fetch_ohlcv("AAPL")
    save_prices(rows)
    logger.info(f"Saved {len(rows)} rows for AAPL")
    return {"status" : "ok", "rows_saved" : len(rows)}


def fetch_ohlcv(symbol: str) -> list[dict]:
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="7d")
    rows=[]
    for timestamp, row in df.iterrows():
        rows.append({
            "time": timestamp,
            "asset_id": symbol,
            "open": row["Open"],
            "high": row["High"],
            "low": row["Low"],
            "close": row["Close"],
            "volume": int(row["Volume"]),
        })
    return rows
    


async def save_prices_async(rows: list[dict]):
    async with async_session() as session:
        for row in rows:
            stmt = insert(PriceData).values(**row).on_conflict_do_nothing()
            await session.execute(stmt)
        await session.commit()

def save_prices(rows: list[dict]):
    asyncio.run(save_prices_async(rows))
