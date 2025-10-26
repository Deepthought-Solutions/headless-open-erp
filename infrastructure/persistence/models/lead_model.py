"""Lead ORM model - infrastructure layer."""

from sqlalchemy import Column, Integer, String, DateTime, func, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from infrastructure.database import Base


class LeadModel(Base):
    """ORM Model for Lead - infrastructure concern."""
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

    fingerprint = relationship("FingerprintModel")
    contact = relationship("ContactModel", back_populates="leads")
    company = relationship("CompanyModel", back_populates="leads")
    status = relationship("LeadStatusModel")
    urgency = relationship("LeadUrgencyModel")
    recommended_pack = relationship("RecommendedPackModel")
    positions = relationship("PositionModel", secondary="lead_positions")
    concerns = relationship("ConcernModel", secondary="lead_concerns")
    attachments = relationship("LeadAttachmentModel", back_populates="lead")
    history = relationship("LeadHistoryModel", back_populates="lead")
    notes = relationship("NoteModel", back_populates="lead")
    modification_logs = relationship("LeadModificationLogModel", back_populates="lead")

    @hybrid_property
    def potential_score(self):
        """Calculate potential score (kept for backwards compatibility with existing queries)."""
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
