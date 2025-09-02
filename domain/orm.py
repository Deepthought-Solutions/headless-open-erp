from sqlalchemy import (
    Column, Integer, String, DateTime, func, JSON, ForeignKey, text, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from infrastructure.database import Base

class LeadStatus(Base):
    __tablename__ = 'lead_statuses'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

class LeadUrgency(Base):
    __tablename__ = 'lead_urgencies'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

class RecommendedPack(Base):
    __tablename__ = 'recommended_packs'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=True)
    job_title = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    leads = relationship("Lead", back_populates="contact")

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    size = Column(Integer, nullable=True)

    leads = relationship("Lead", back_populates="company")

class Position(Base):
    __tablename__ = "positions"
    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True, nullable=False)

class Sector(Base):
    __tablename__ = "sectors"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

class Concern(Base):
    __tablename__ = "concerns"
    id = Column(Integer, primary_key=True)
    label = Column(String, unique=True)

class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True, index=True)
    submission_date = Column(DateTime(timezone=True), server_default=func.now())
    estimated_users = Column(Integer, nullable=True)
    problem_summary = Column(Text, nullable=True)

    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)

    recommended_pack_id = Column(Integer, ForeignKey("recommended_packs.id"), nullable=True)
    maturity_score = Column(Integer, nullable=True)
    urgency_id = Column(Integer, ForeignKey("lead_urgencies.id"), nullable=True)
    status_id = Column(Integer, ForeignKey("lead_statuses.id"), nullable=False)
    fingerprint_visitor_id = Column(String, ForeignKey("fingerprints.visitorId"), nullable=True)
    altcha_solution = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    fingerprint = relationship("Fingerprint")
    contact = relationship("Contact", back_populates="leads")
    company = relationship("Company", back_populates="leads")
    status = relationship("LeadStatus")
    urgency = relationship("LeadUrgency")
    recommended_pack = relationship("RecommendedPack")
    positions = relationship("Position", secondary="lead_positions")
    concerns = relationship("Concern", secondary="lead_concerns")
    attachments = relationship("LeadAttachment", back_populates="lead")
    history = relationship("LeadHistory", back_populates="lead")
    notes = relationship("Note", back_populates="lead")
    modification_logs = relationship("LeadModificationLog", back_populates="lead")

    @hybrid_property
    def potential_score(self):
        score = 0
        if self.company and self.company.size:
            if self.company.size > 1000:
                score += 3
            elif self.company.size > 250:
                score += 2
            else:
                score += 1

        if self.urgency and self.urgency.name == "immédiat":
            score += 3
        elif self.urgency and self.urgency.name == "ce mois":
            score += 2

        if self.contact and self.contact.job_title:
            if any(role in self.contact.job_title.lower() for role in ['ceo', 'cto', 'manager', 'director']):
                score += 2

        return score

class LeadPosition(Base):
    __tablename__ = "lead_positions"
    lead_id = Column(Integer, ForeignKey("leads.id"), primary_key=True)
    position_id = Column(Integer, ForeignKey("positions.id"), primary_key=True)

class LeadConcern(Base):
    __tablename__ = "lead_concerns"
    lead_id = Column(Integer, ForeignKey("leads.id"), primary_key=True)
    concern_id = Column(Integer, ForeignKey("concerns.id"), primary_key=True)

class LeadAttachment(Base):
    __tablename__ = "lead_attachments"
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    lead = relationship("Lead", back_populates="attachments")

class LeadHistory(Base):
    __tablename__ = "lead_history"
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    action = Column(String, nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    lead = relationship("Lead", back_populates="history")

class LeadModificationLog(Base):
    __tablename__ = "lead_modification_logs"
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    field_name = Column(String, nullable=False)
    old_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)
    changed_at = Column(DateTime(timezone=True), server_default=func.now())

    lead = relationship("Lead", back_populates="modification_logs")

class NoteReason(Base):
    __tablename__ = 'note_reasons'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)

class Note(Base):
    __tablename__ = 'notes'
    id = Column(Integer, primary_key=True, index=True)
    note = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    author_name = Column(String, nullable=False)
    lead_id = Column(Integer, ForeignKey('leads.id'), nullable=False)
    reason_id = Column(Integer, ForeignKey('note_reasons.id'), nullable=False)

    lead = relationship("Lead", back_populates="notes")
    reason = relationship("NoteReason")

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    visitorId = Column(String, ForeignKey("fingerprints.visitorId"), nullable=False)
    page = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))

class Fingerprint(Base):
    __tablename__ = 'fingerprints'
    visitorId = Column(String, primary_key=True, index=True)
    components = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
