"""Price data model — OHLCV time-series stored in TimescaleDB."""

from sqlalchemy import Column, String, Float, DateTime, BigInteger
from app.database import Base


class PriceData(Base):
    __tablename__ = "price_data"

    # TimescaleDB hypertable — time + asset_id form the composite key
    time = Column(DateTime(timezone=True), primary_key=True, nullable=False)
    asset_id = Column(String, primary_key=True, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(BigInteger, nullable=False, default=0)
