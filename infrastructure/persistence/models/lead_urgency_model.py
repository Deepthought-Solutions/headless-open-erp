"""Lead Urgency ORM model - infrastructure layer."""

from sqlalchemy import Column, Integer, String
from infrastructure.database import Base


class LeadUrgencyModel(Base):
    """ORM Model for Lead Urgency - infrastructure concern."""
    __tablename__ = 'lead_urgencies'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
