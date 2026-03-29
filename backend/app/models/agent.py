"""Agent model — to be implemented in Phase 1."""

import enum
import uuid
from sqlalchemy import Column, String, DateTime, Enum as SAEnum, Table, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base
class AgentStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"

agent_watchlist = Table(
    "agent_watchlist",
    Base.metadata,
    Column("agent_id", String, ForeignKey("agents.id", ondelete="CASCADE"), primary_key=True),
    Column("asset_id", String, ForeignKey("assets.id", ondelete="CASCADE"), primary_key=True),
)

class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    status = Column(SAEnum(AgentStatus), nullable=False, default=AgentStatus.ACTIVE)
    config_json = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    watchlist = relationship("Asset", secondary=agent_watchlist, lazy="selectin")
    beliefs = relationship("BeliefState", back_populates="agent", lazy="dynamic")
    