"""Asset model — stocks, ETFs, and crypto."""

from sqlalchemy import Column, String, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.database import Base
import enum


class AssetType(str, enum.Enum):
    STOCK = "stock"
    ETF = "etf"
    CRYPTO = "crypto"


class Asset(Base):
    __tablename__ = "assets"

    id = Column(String, primary_key=True)  # e.g. "AAPL", "BTC-USD"
    symbol = Column(String, nullable=False, unique=True, index=True)
    name = Column(String, nullable=False)
    asset_type = Column(SAEnum(AssetType), nullable=False)
    exchange = Column(String, nullable=True)
    metadata_json = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
