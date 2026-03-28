"""Embedding pipeline — chunks documents and stores vectors in pgvector. Phase 2."""

from app.workers.celery_app import celery_app
import asyncio
import logging

from sqlalchemy import select, update
from app.database import async_session
from app.models.article import Article
from openai import OpenAI
from app.config import settings

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.OPENAI_API_KEY)


async def _embed_all():
    articles = await get_unembedded_articles_async()
    for article in articles:
        text = f"{article.title}. {article.summary or ''}"
        embedding = get_embedding(text)
        await save_embedding_async(article.id, embedding)
    return len(articles)


@celery_app.task(name="app.workers.embedding_pipeline.embed_document")
def embed_document():
    count = asyncio.run(_embed_all())
    logger.info(f"Embedded {count} articles")
    return {"status": "ok", "embedded": count}




async def get_unembedded_articles_async() -> list[dict]:
    async with async_session() as session:
        result = await session.execute(
            select(Article).where(Article.embedding == None).limit(50)
        )
        return result.scalars().all()
    
def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding


async def save_embedding_async(article_id: str, embedding: list[float]):
    async with async_session() as session:
        await session.execute(
            update(Article).where(Article.id == article_id).values(embedding=embedding)
        )
        await session.commit()





