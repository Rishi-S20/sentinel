"""Agent runner — orchestrates a full reasoning cycle for all active agents."""

import asyncio
import logging
from sqlalchemy import select
from app.workers.celery_app import celery_app
from app.database import async_session
from app.models.agent import Agent
from app.models.asset import Asset  # noqa: F401 — required for SQLAlchemy to resolve Agent.watchlist relationship
from app.core.memory_manager import assemble_context
from app.core.reasoning_chain import run_reasoning_chain
from app.core.belief_engine import get_latest_belief, save_belief
from app.core.anomaly_detector import detect_anomaly
from app.workers.embedding_pipeline import get_embedding
from app.core.briefing_generator import generate_briefing




logger = logging.getLogger(__name__)

async def _generate_all_briefings():
    async with async_session() as session:
        result = await session.execute(
            select(Agent).where(Agent.status == "active")
        )
        agents = result.scalars().all()
    for agent in agents:
        await asyncio.get_event_loop().run_in_executor(None, generate_briefing, agent.id)
    return len(agents)


async def run_agent(agent: Agent):
    for asset in agent.watchlist:
        try:
            # 1. Generate a query embedding from the asset symbol to retrieve relevant articles
            query_embedding = get_embedding(asset.id)

            # 2. Assemble context — prices + relevant articles + current belief
            context = await assemble_context(agent.id, asset.id, query_embedding)

            # 3. Run reasoning chain — call Gemini, get new belief
            new_belief = run_reasoning_chain(context)

            # 4. Detect anomalies before saving
            previous = await get_latest_belief(agent.id, asset.id)
            anomaly = detect_anomaly(previous, new_belief)
            if anomaly:
                logger.warning(f"[{agent.id}] Anomaly on {asset.id}: {anomaly['message']}")

            # 5. Save new belief state (always append, never update)
            await save_belief(
                agent_id=agent.id,
                asset_id=asset.id,
                conviction=new_belief["conviction"],
                thesis=new_belief["thesis"],
                key_factors=new_belief.get("key_factors", []),
                evidence_refs=new_belief.get("evidence_refs", []),
            )

            logger.info(f"[{agent.id}] Updated belief for {asset.id} — conviction: {new_belief['conviction']:.2f}")

        except Exception as e:
            logger.error(f"[{agent.id}] Failed on asset {asset.id}: {e}", exc_info=True)


async def _run_all_agents():
    async with async_session() as session:
        result = await session.execute(
            select(Agent).where(Agent.status == "active")
        )
        agents = result.scalars().all()

    for agent in agents:
        await run_agent(agent)

    return len(agents)


@celery_app.task(name="app.workers.agent_runner.run_due_agents")
def run_due_agents():
    count = asyncio.run(_run_all_agents())
    logger.info(f"Ran reasoning cycle for {count} agents")
    return {"status": "ok", "agents_run": count}

@celery_app.task(name="app.workers.agent_runner.generate_all_briefings")
def generate_all_briefings():
    count = asyncio.run(_generate_all_briefings())
    logger.info(f"Generated briefings for {count} agents")
    return {"status": "ok", "agents": count}
