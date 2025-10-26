"""Lead Modification Log ORM model - infrastructure layer."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from infrastructure.database import Base


class LeadModificationLogModel(Base):
    """ORM Model for Lead Modification Log - infrastructure concern."""
    __tablename__ = "lead_modification_logs"

    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    field_name = Column(String, nullable=False)
    old_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())

    lead = relationship("LeadModel", back_populates="modification_logs")
