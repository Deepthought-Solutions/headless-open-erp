"""Lead Attachment ORM model - infrastructure layer."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from infrastructure.database import Base


class LeadAttachmentModel(Base):
    """ORM Model for Lead Attachment - infrastructure concern."""
    __tablename__ = "lead_attachments"

    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    lead = relationship("LeadModel", back_populates="attachments")
