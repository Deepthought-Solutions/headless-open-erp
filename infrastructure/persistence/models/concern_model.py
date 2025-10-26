"""Concern ORM model - infrastructure layer."""

from sqlalchemy import Column, Integer, String
from infrastructure.database import Base


class ConcernModel(Base):
    """ORM Model for Concern - infrastructure concern."""
    __tablename__ = "concerns"

    id = Column(Integer, primary_key=True)
    label = Column(String, unique=True)
