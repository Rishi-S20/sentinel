"""News fetcher — pulls company news from Finnhub. Phase 2."""

from app.workers.celery_app import celery_app
import logging
from sqlalchemy import select, distinct
from sqlalchemy.dialects.postgresql import insert
from app.database import sync_session
from app.models.article import Article
from app.models.agent import Agent, agent_watchlist

import finnhub
from datetime import datetime, timezone, timedelta
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


def save_articles(rows: list[dict]):
    with sync_session() as session:
        stmt = insert(Article).values(rows).on_conflict_do_nothing(index_elements=["url"])
        session.execute(stmt)
        session.commit()


@celery_app.task(name="app.workers.news_fetcher.fetch_news")
def fetch_news():
    symbols = get_tracked_symbols()
    total = 0
    for symbol in symbols:
        rows = fetch_articles(symbol)
        if not rows:
            logger.warning(f"No articles for {symbol}")
            continue
        save_articles(rows)
        total += len(rows)
        logger.info(f"Saved {len(rows)} articles for {symbol}")
    return {"status": "ok", "articles_saved": total}


def fetch_articles(symbol: str) -> list[dict]:
    today = datetime.now(timezone.utc)
    from_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")

    try:
        news = finnhub_client.company_news(symbol, _from=from_date, to=to_date)
    except Exception as e:
        logger.warning(f"Finnhub error for {symbol}: {e}")
        return []

    rows = []
    for article in news[:20]:
        url = article.get("url", "")
        if not url:
            continue
        rows.append({
            "asset_id": symbol,
            "source": article.get("source", ""),
            "url": url,
            "title": article.get("headline", ""),
            "summary": article.get("summary"),
            "published_at": datetime.fromtimestamp(article["datetime"], tz=timezone.utc),
            "sentiment_score": None,
            "embedding": None,
        })
    return rows
