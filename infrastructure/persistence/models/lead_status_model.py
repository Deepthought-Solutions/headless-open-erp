"""Lead Status ORM model - infrastructure layer."""

from sqlalchemy import Column, Integer, String
from infrastructure.database import Base


class LeadStatusModel(Base):
    """ORM Model for Lead Status - infrastructure concern."""
    __tablename__ = 'lead_statuses'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
