"""Sector ORM model - infrastructure layer."""

from sqlalchemy import Column, Integer, String
from infrastructure.database import Base


class SectorModel(Base):
    """ORM Model for Sector - infrastructure concern."""
    __tablename__ = "sectors"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
