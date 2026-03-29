"""Briefing generator — to be implemented in Phase 4."""

import asyncio
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from app.database import async_session
from app.models.belief import BeliefState
from app.models.briefing import Briefing
from app.workers.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)

async def get_recent_beliefs(agent_id: str) -> list[BeliefState]:
    """Get the latest belief state for each asset the agent tracks."""
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    async with async_session() as session:
        result = await session.execute(
            select(BeliefState)
            .where(BeliefState.agent_id == agent_id, BeliefState.created_at >= since)
            .order_by(BeliefState.asset_id, BeliefState.created_at.desc())
        )
        beliefs = result.scalars().all()


        seen = {}
        for b in beliefs:
            if b.asset_id not in seen:
                seen[b.asset_id] = b
        return list(seen.values())


def render_markdown(agent_id: str, beliefs: list[BeliefState]) -> str:
    """Build the markdown briefing from a list of belief states."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [f"# Sentinel Briefing - {now}\n"]

    if not beliefs:
        lines.append("_No belief updates int eh last 24 hours._")
        return "\n".join(lines)
    
    for b in beliefs:
        conviction_pct = int(b.conviction * 100)
        if b.conviction >= 0.6:
            sentiment = "Bullish"
        elif b.conviction <= 0.4:
            sentiment = "Bearish"
        else:
            sentiment = "Neutral"

        lines.append(f"## {b.asset_id} — {sentiment} ({conviction_pct}%)\n")
        lines.append(f"{b.thesis}\n")

        if b.key_factors:
            lines.append("**Key Factors:**")
            for f in b.key_factors:
                icon = "+" if f["signal"] == "bullish" else "-" if f["signal"] == "bearish" else "~"
                lines.append(f"- [{icon}] {f['factor']} (weight: {f['weight']})")
            lines.append("")

    return "\n".join(lines)


async def _generate_briefing(agent_id: str) -> str:
    beliefs = await get_recent_beliefs(agent_id)
    content_md = render_markdown(agent_id, beliefs)
    all_refs = [ref for b in beliefs for ref in (b.evidence_refs or [])]

    async with async_session() as session:
        briefing = Briefing(
            agent_id=agent_id,
            content_md=content_md,
            sources=all_refs,
        )
        session.add(briefing)
        await session.commit()

    return content_md


@celery_app.task(name="app.core.briefing_generator.generate_briefing")
def generate_briefing(agent_id: str):
    content_md = asyncio.run(_generate_briefing(agent_id))
    logger.info(f"Generated briefing for agent {agent_id}")
    return {"status": "ok", "preview": content_md[:200]}

            