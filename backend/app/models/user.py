"""User model — to be implemented in Phase 1."""

import enum
from sqlalchemy import Column, String, DateTime, Enum as SAEnum
from sqlalchemy.sql import func
from app.database import Base

class PlanTier(str, enum.Enum):
    FREE="free"
    PRO="pro"
    TEAM="team"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, nullable=False, unique=True, index=True)
    name = Column(String, nullable=False)
    plan_tier = Column(SAEnum(PlanTier), nullable=False, default=PlanTier.FREE)
    created_at = Column(DateTime(timezone=True), server_default=func.now())




    


