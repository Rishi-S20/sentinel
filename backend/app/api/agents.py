"""Agent routes — to be implemented in Phase 1."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from app.database import async_session
from app.models.agent import Agent, agent_watchlist
from app.models.asset import Asset, AssetType
from app.api.auth import get_current_user
from pydantic import BaseModel

from app.models.belief import BeliefState
from app.models.briefing import Briefing
from app.models.user import User
from sqlalchemy.dialects.postgresql import insert as pg_insert


router = APIRouter()

class CreateAgentRequest(BaseModel):
    name: str
    asset_symbols: list[str]


@router.get("")
async def list_agents(user=Depends(get_current_user)):
    async with async_session() as session:
        result = await session.execute(
            select(Agent).where(Agent.user_id == user["sub"])
        )
        agents = result.scalars().all()
        return [
            {
                "id" : a.id,
                "name" : a.name,
                "status" : a.status,
                "created_at": a.created_at,
            }
            for a in agents
        ]


@router.post("")
async def create_agent(body: CreateAgentRequest, user=Depends(get_current_user)):
    async with async_session() as session:
        # Upsert user from Stack Auth JWT claims
        await session.execute(
            pg_insert(User).values(
                id=user["sub"],
                email=user.get("email", ""),
                name=user.get("name") or user.get("email", ""),
            ).on_conflict_do_nothing(index_elements=["id"])
        )
        await session.flush()

        agent = Agent(user_id=user["sub"], name=body.name)
        session.add(agent)
        await session.flush()

        for symbol in body.asset_symbols:
            asset = await session.get(Asset, symbol.upper())
            if not asset:
                asset = Asset(
                    id=symbol.upper(),
                    symbol=symbol.upper(),
                    name=symbol.upper(),
                    asset_type=AssetType.STOCK,
                )
                session.add(asset)
                await session.flush()
            
            await session.execute(
                agent_watchlist.insert().values(agent_id=agent.id, asset_id=asset.id)
            )
        await session.commit()
        return {"id": agent.id, "name": agent.name, "status": agent.status}



@router.get("/{agent_id}/beliefs")
async def list_beliefs(agent_id: str, user=Depends(get_current_user)):
    async with async_session() as session:
        # Verify agent belongs to user
        agent = await session.get(Agent, agent_id)
        if not agent or agent.user_id != user["sub"]:
            raise HTTPException(status_code=404, detail="Agent not found")

        result = await session.execute(
            select(BeliefState)
            .where(BeliefState.agent_id == agent_id)
            .order_by(BeliefState.created_at.desc())
            .limit(50)
        )
        beliefs = result.scalars().all()
        return [
            {
                "id": b.id,
                "asset_id": b.asset_id,
                "conviction": b.conviction,
                "thesis": b.thesis,
                "key_factors": b.key_factors,
                "created_at": b.created_at,
            }
            for b in beliefs
        ]


@router.get("/{agent_id}/briefings")
async def list_briefings(agent_id: str, user=Depends(get_current_user)):
    async with async_session() as session:
        agent = await session.get(Agent, agent_id)
        if not agent or agent.user_id != user["sub"]:
            raise HTTPException(status_code=404, detail="Agent not found")

        result = await session.execute(
            select(Briefing)
            .where(Briefing.agent_id == agent_id)
            .order_by(Briefing.created_at.desc())
            .limit(10)
        )
        briefings = result.scalars().all()
        return [
            {
                "id": b.id,
                "content_md": b.content_md,
                "created_at": b.created_at,
            }
            for b in briefings
        ]
