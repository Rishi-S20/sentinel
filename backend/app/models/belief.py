"""Belief state model — to be implemented in Phase 3."""

import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.database import Base


class BeliefState(Base):
    __tablename__ = "belief_states"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    asset_id = Column(String, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)

    # Core belief — 0.0 = max bearish, 1.0 = max bullish
    conviction = Column(Float, nullable=False)
    thesis = Column(Text, nullable=False)

    
    key_factors = Column(JSONB, default=[])

    evidence_refs = Column(JSONB, default=[])

    created_at = Column(DateTime(timezone=True), server_default=func.now())


