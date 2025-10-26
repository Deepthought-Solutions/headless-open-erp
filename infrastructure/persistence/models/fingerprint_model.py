"""Fingerprint ORM model - infrastructure layer."""

from sqlalchemy import Column, String, DateTime, func, JSON
from infrastructure.database import Base


class FingerprintModel(Base):
    """SQLAlchemy ORM model for fingerprints - infrastructure concern."""

    __tablename__ = 'fingerprints'

    visitorId = Column(String, primary_key=True, index=True)
    components = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
