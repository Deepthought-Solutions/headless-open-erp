"""Contact ORM model - infrastructure layer."""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, func
from sqlalchemy.orm import relationship
from infrastructure.database import Base


class ContactModel(Base):
    """ORM Model for Contact - infrastructure concern."""
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    job_title = Column(String, nullable=True)
    conscent = Column(Boolean, nullable=False, server_default='0')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    leads = relationship("LeadModel", back_populates="contact")
