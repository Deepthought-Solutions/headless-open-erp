"""Lead association models - infrastructure layer."""

from sqlalchemy import Column, Integer, ForeignKey
from infrastructure.database import Base


class LeadPositionModel(Base):
    """ORM Model for Lead-Position association."""
    __tablename__ = "lead_positions"

    lead_id = Column(Integer, ForeignKey("leads.id"), primary_key=True)
    position_id = Column(Integer, ForeignKey("positions.id"), primary_key=True)


class LeadConcernModel(Base):
    """ORM Model for Lead-Concern association."""
    __tablename__ = "lead_concerns"

    lead_id = Column(Integer, ForeignKey("leads.id"), primary_key=True)
    concern_id = Column(Integer, ForeignKey("concerns.id"), primary_key=True)
