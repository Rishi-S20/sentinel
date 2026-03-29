"""Memory manager (RAG) — to be implemented in Phase 3."""


from sqlalchemy import select, text
from app.database import async_session
from app.models.article import Article
from app.models.price_data import PriceData
from app.core.belief_engine import get_latest_belief


async def get_recent_prices(asset_id: str, days: int = 7) -> list[dict]:
    async with async_session() as session:
        result = await session.execute(
            text("""
                 SELECT time, open, high, low, close, volume
                 FROM price_data
                 WHERE asset_id = :asset_id
                    AND time >= NOW() - INTERVAL ':days days'
                ORDER BY time DESC          
            """),
            {"asset_id": asset_id, "days": days},
        )
        rows = result.mappings().all()
        return [dict(r) for r in rows]
    

async def get_relevant_articles(asset_id: str, query_embedding: list[float], top_k: int = 10) -> list[dict]:
    async with async_session() as session:
        result = await session.execute(
            text("""
                SELECT id, title, summary, source, published_at,
                       1 - (embedding <=> CAST(:embedding AS vector)) AS similarity
                FROM articles
                WHERE asset_id = :asset_id
                  AND embedding IS NOT NULL
                ORDER BY embedding <=> CAST(:embedding AS vector)
                LIMIT :top_k
            """),
            {"asset_id": asset_id, "embedding": str(query_embedding), "top_k": top_k},
        )
        rows = result.mappings().all()
        return [dict(r) for r in rows]
    

async def assemble_context(agent_id: str, asset_id: str, query_embedding: list[float]) -> dict:
    """Build the full context dict passed to the reasoning chain."""
    prices = await get_recent_prices(asset_id)
    articles = await get_relevant_articles(asset_id, query_embedding)
    current_belief = await get_latest_belief(agent_id, asset_id)

    return {
        "asset_id": asset_id,
        "prices": prices,
        "articles": articles,
        "current_belief": {
            "conviction": current_belief.conviction,
            "thesis": current_belief.thesis,
            "key_factors": current_belief.key_factors,
        } if current_belief else None,
    }