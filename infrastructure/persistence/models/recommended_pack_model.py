"""Recommended Pack ORM model - infrastructure layer."""

from sqlalchemy import Column, Integer, String
from infrastructure.database import Base


class RecommendedPackModel(Base):
    """ORM Model for Recommended Pack - infrastructure concern."""
    __tablename__ = 'recommended_packs'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
