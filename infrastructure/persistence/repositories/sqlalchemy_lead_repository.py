"""SQLAlchemy implementation of LeadRepository."""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from domain.repositories.lead_repository import LeadRepository
from domain.entities.lead import Lead
from infrastructure.persistence.models import LeadModel as LeadORM
from infrastructure.persistence.mappers.lead_mapper import LeadMapper


class SqlAlchemyLeadRepository(LeadRepository):
    """Concrete repository implementation using SQLAlchemy."""

    def __init__(self, session: Session):
        self._session = session

    def save(self, lead: Lead) -> Lead:
        """Persist a new lead."""
        model = LeadMapper.to_model(lead)
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)

        # Load all relationships
        self._session.refresh(model, [
            'contact', 'company', 'status', 'urgency',
            'recommended_pack', 'positions', 'concerns'
        ])

        return LeadMapper.to_domain(model)

    def find_by_id(self, lead_id: int) -> Optional[Lead]:
        """Find lead by ID with all relationships loaded."""
        model = self._session.query(LeadORM).options(
            joinedload(LeadORM.contact),
            joinedload(LeadORM.company),
            joinedload(LeadORM.status),
            joinedload(LeadORM.urgency),
            joinedload(LeadORM.recommended_pack),
            joinedload(LeadORM.positions),
            joinedload(LeadORM.concerns)
        ).filter(
            LeadORM.id == lead_id
        ).one_or_none()

        return LeadMapper.to_domain(model) if model else None

    def find_all(self) -> List[Lead]:
        """Get all leads with relationships."""
        models = self._session.query(LeadORM).options(
            joinedload(LeadORM.contact),
            joinedload(LeadORM.company),
            joinedload(LeadORM.status),
            joinedload(LeadORM.urgency),
            joinedload(LeadORM.recommended_pack),
            joinedload(LeadORM.positions),
            joinedload(LeadORM.concerns)
        ).all()

        return [LeadMapper.to_domain(m) for m in models]

    def update(self, lead: Lead) -> Lead:
        """Update existing lead."""
        model = self._session.query(LeadORM).filter(
            LeadORM.id == lead.id
        ).one_or_none()

        if not model:
            raise ValueError(f"Lead {lead.id} not found")

        # Update fields
        model.submission_date = lead.submission_date
        model.estimated_users = lead.estimated_users
        model.problem_summary = lead.problem_summary
        model.maturity_score = lead.maturity_score
        model.altcha_solution = lead.altcha_solution
        model.fingerprint_visitor_id = lead.fingerprint_visitor_id
        model.updated_at = lead.updated_at

        # Update foreign keys
        model.contact_id = lead.contact.id if lead.contact else None
        model.company_id = lead.company.id if lead.company else None
        model.status_id = lead.status.id if lead.status else None
        model.urgency_id = lead.urgency.id if lead.urgency else None
        model.recommended_pack_id = lead.recommended_pack.id if lead.recommended_pack else None

        self._session.commit()
        self._session.refresh(model, [
            'contact', 'company', 'status', 'urgency',
            'recommended_pack', 'positions', 'concerns'
        ])

        return LeadMapper.to_domain(model)

    def delete(self, lead_id: int) -> bool:
        """Delete a lead."""
        model = self._session.query(LeadORM).filter(
            LeadORM.id == lead_id
        ).one_or_none()

        if not model:
            return False

        self._session.delete(model)
        self._session.commit()
        return True
