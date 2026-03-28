"""Article model — news articles fetched from NewsAPI."""

from sqlalchemy import Column, String, Float, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.database import Base
import uuid


class Article(Base):
    __tablename__ = "articles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    asset_id = Column(String, nullable=True, index=True)  # which asset this is about
    source = Column(String, nullable=False)               # e.g. "newsapi"
    url = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    sentiment_score = Column(Float, nullable=True)        # -1.0 to 1.0
    published_at = Column(DateTime(timezone=True), nullable=True)
    embedding = Column(Vector(1536), nullable=True)       # OpenAI embedding
    created_at = Column(DateTime(timezone=True), server_default=func.now())
