"""News fetcher — pulls articles from NewsAPI and Finnhub. Phase 2."""

from app.workers.celery_app import celery_app
import logging

import asyncio
from sqlalchemy import select, distinct
from sqlalchemy.dialects.postgresql import insert
from app.database import async_session
from app.models.article import Article
from app.models.agent import Agent, agent_watchlist

import requests
from app.config import settings
from datetime import datetime

logger = logging.getLogger(__name__)


async def get_tracked_symbols() -> list[str]:
    async with async_session() as session:
        result = await session.execute(
            select(distinct(agent_watchlist.c.asset_id))
            .join(Agent, Agent.id == agent_watchlist.c.agent_id)
            .where(Agent.status == "active")
        )
        return [row[0] for row in result.all()]


async def save_articles_async(rows: list[dict]):
    if not rows:
        return
    async with async_session() as session:
        stmt = insert(Article).values(rows).on_conflict_do_nothing(index_elements=["url"])
        await session.execute(stmt)
        await session.commit()

def save_articles(rows: list[dict]):
    asyncio.run(save_articles_async(rows))

@celery_app.task(name="app.workers.news_fetcher.fetch_news")
def fetch_news():
    symbols = asyncio.run(get_tracked_symbols())
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
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": symbol,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 20,
        "apiKey": settings.NEWS_API_KEY,
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()


    rows = []
    for article in data.get("articles", []):
        rows.append({
            "asset_id": symbol,
            "source": article["source"]["name"],
            "url": article["url"],
            "title": article["title"],
            "summary": article.get("description"),
            "published_at": datetime.fromisoformat(
                article["publishedAt"].replace("Z", "+00:00")
            ),
            "sentiment_score": None,  # filled in later by embedding pipeline
            "embedding": None,        # filled in later by embedding pipeline
        })
    return rows
