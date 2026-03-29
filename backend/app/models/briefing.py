
"""Briefing model — AI-generated markdown summary of agent belief changes."""

import uuid
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.database import Base


class Briefing(Base):
    __tablename__ = "briefings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String, nullable=False, index=True)
    content_md = Column(Text, nullable=False)
    sources = Column(JSONB, default=[])  # list of article IDs referenced
    created_at = Column(DateTime(timezone=True), server_default=func.now())
