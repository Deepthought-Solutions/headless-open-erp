"""Lead History ORM model - infrastructure layer."""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from infrastructure.database import Base


class LeadHistoryModel(Base):
    """ORM Model for Lead History - infrastructure concern."""
    __tablename__ = "lead_history"

    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    action = Column(String, nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    lead = relationship("LeadModel", back_populates="history")
