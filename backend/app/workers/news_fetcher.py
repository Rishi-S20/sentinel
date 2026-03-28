"""News fetcher — pulls articles from NewsAPI and Finnhub. Phase 2."""

from app.workers.celery_app import celery_app
import logging

import asyncio
from sqlalchemy.dialects.postgresql import insert
from app.database import async_session
from app.models.article import Article

import requests
from app.config import settings
from datetime import datetime

logger = logging.getLogger(__name__)


async def save_articles_async(rows: list[dict]):
    async with async_session() as session:
        for row in rows:
            stmt = insert(Article).values(**row).on_conflict_do_nothing(index_elements=["url"])
            await session.execute(stmt)
        await session.commit()

def save_articles(rows: list[dict]):
    asyncio.run(save_articles_async(rows))

@celery_app.task(name="app.workers.news_fetcher.fetch_news")
def fetch_news():
    item = "AAPL"
    rows = fetch_articles(item)
    if not rows:
        logger.warning(f"fetch_articles returned no data for {item}")
        return {"status": "no_data"}
    save_articles(rows)
    logger.info(f"Saved {len(rows)} articles for {item}")
    return {"status": "ok", "articles_saved": len(rows)}

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
