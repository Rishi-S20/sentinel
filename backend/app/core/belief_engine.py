"""Belief engine — to be implemented in Phase 3."""

from sqlalchemy import select
from app.database import async_session
from app.models.belief import BeliefState

async def get_latest_belief(agent_id: str, asset_id: str) -> BeliefState | None:
    async with async_session() as session:
        result = await session.execute(
            select(BeliefState)
            .where(BeliefState.agent_id == agent_id, BeliefState.asset_id == asset_id)
            .order_by(BeliefState.created_at.desc())
            .limit(1)
        )
        return result.scalars().first()
    

async def save_belief(
        agent_id: str,
        asset_id: str,
        conviction: float,
        thesis: str,
        key_factors: list[dict],
        evidence_refs: list[dict],
) -> BeliefState:
    async with async_session() as session:
        belief = BeliefState(
            agent_id=agent_id,
            asset_id=asset_id,
            conviction=conviction,
            thesis=thesis,
            key_factors=key_factors,
            evidence_refs=evidence_refs,
        )
        session.add(belief)
        await session.commit()
        await session.refresh(belief)
        return belief