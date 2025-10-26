"""Note ORM model - infrastructure layer."""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from infrastructure.database import Base


class NoteReasonModel(Base):
    """ORM Model for Note Reason - infrastructure concern."""
    __tablename__ = 'note_reasons'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)


class NoteModel(Base):
    """ORM Model for Note - infrastructure concern."""
    __tablename__ = 'notes'

    id = Column(Integer, primary_key=True, index=True)
    note = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    author_name = Column(String, nullable=False)
    lead_id = Column(Integer, ForeignKey('leads.id'), nullable=False)
    reason_id = Column(Integer, ForeignKey('note_reasons.id'), nullable=False)

    lead = relationship("LeadModel", back_populates="notes")
    reason = relationship("NoteReasonModel")
