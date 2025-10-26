"""Lead application service - refactored to use repository pattern."""

import logging
from datetime import datetime
from typing import List, Optional

from domain.repositories.lead_repository import LeadRepository
from domain.repositories.contact_repository import ContactRepository
from domain.repositories.company_repository import CompanyRepository
from domain.repositories.position_repository import PositionRepository
from domain.repositories.concern_repository import ConcernRepository
from domain.repositories.note_repository import NoteRepository
from domain.entities.lead import Lead, LeadStatus, LeadUrgency, RecommendedPack
from domain.entities.contact import Contact
from domain.entities.company import Company
from domain.entities.position import Position
from domain.entities.concern import Concern
from domain.entities.note import Note, NoteReason
from domain.services.lead_scoring_service import LeadScoringService
from domain.contact import LeadPayload, LeadUpdateRequest
# Still need ORM models for LeadPosition, LeadConcern, LeadModificationLog
from infrastructure.persistence.models import (
    LeadPositionModel as LeadPosition,
    LeadConcernModel as LeadConcern,
    LeadModificationLogModel as LeadModificationLog,
    LeadStatusModel as LeadStatusORM,
    LeadUrgencyModel as LeadUrgencyORM,
    RecommendedPackModel as RecommendedPackORM,
    LeadModel as LeadORM
)
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class LeadService:
    """Application service for lead operations - uses repository pattern."""

    def __init__(
        self,
        session: Session,  # Still needed for LeadPosition/LeadConcern/LeadModificationLog
        lead_repository: LeadRepository,
        contact_repository: ContactRepository,
        company_repository: CompanyRepository,
        position_repository: PositionRepository,
        concern_repository: ConcernRepository,
        note_repository: NoteRepository,
        scoring_service: LeadScoringService
    ):
        self._session = session
        self._lead_repo = lead_repository
        self._contact_repo = contact_repository
        self._company_repo = company_repository
        self._position_repo = position_repository
        self._concern_repo = concern_repository
        self._note_repo = note_repository
        self._scoring_service = scoring_service

    def _get_or_create_contact(
        self, name: str, email: str, phone: str, job_title: str, conscent: bool = False
    ) -> Contact:
        """Get or create a contact."""
        contact = self._contact_repo.find_by_email(email)
        if not contact:
            contact = Contact(
                id=None,
                name=name,
                email=email,
                phone=phone,
                job_title=job_title,
                conscent=conscent,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            contact = self._contact_repo.save(contact)
        else:
            # Update contact info if it has changed
            contact.name = name
            contact.phone = phone
            contact.job_title = job_title
            contact.conscent = conscent
            contact.updated_at = datetime.now()
            contact = self._contact_repo.update(contact)

        return contact

    def _get_or_create_company(self, company_name: str, size: int) -> Company:
        """Get or create a company."""
        company = self._company_repo.find_by_name(company_name)
        if not company:
            company = Company(
                id=None,
                name=company_name,
                size=size
            )
            company = self._company_repo.save(company)
        else:
            company.size = size
            company = self._company_repo.update(company)

        return company

    def _get_or_create_position(self, position_title: str) -> Position:
        """Get or create a position."""
        position = self._position_repo.find_by_title(position_title)
        if not position:
            position = Position(
                id=None,
                title=position_title
            )
            position = self._position_repo.save(position)

        return position

    def _get_or_create_concern(self, concern_label: str) -> Concern:
        """Get or create a concern."""
        concern = self._concern_repo.find_by_label(concern_label)
        if not concern:
            concern = Concern(
                id=None,
                label=concern_label
            )
            concern = self._concern_repo.save(concern)

        return concern

    def create_lead(self, lead_payload: LeadPayload, altcha: str, visitor_id: str) -> LeadORM:
        """Create a new lead - returns ORM model for API compatibility."""
        try:
            # Get or create contact and company
            contact = self._get_or_create_contact(
                name=lead_payload.name,
                email=lead_payload.email,
                phone=lead_payload.phone,
                job_title=lead_payload.job_title,
                conscent=lead_payload.conscent
            )

            company = self._get_or_create_company(
                company_name=lead_payload.company_name,
                size=lead_payload.company_size
            )

            # Calculate maturity score using domain service
            maturity_score = self._scoring_service.calculate_maturity_score(lead_payload)

            # Get recommended pack using domain service
            pack_name = self._scoring_service.recommend_pack(lead_payload.concerns)
            recommended_pack_orm = self._session.query(RecommendedPackORM).filter_by(name=pack_name).first()
            if not recommended_pack_orm:
                logger.error(f"Recommended pack '{pack_name}' not found in the database.")
                recommended_pack_orm = self._session.query(RecommendedPackORM).filter_by(name='conformité').first()

            recommended_pack = RecommendedPack(
                id=recommended_pack_orm.id,
                name=recommended_pack_orm.name
            ) if recommended_pack_orm else None

            # Get urgency
            urgency_orm = self._session.query(LeadUrgencyORM).filter_by(name=lead_payload.urgency).first()
            if not urgency_orm:
                logger.warning(f"Urgency '{lead_payload.urgency}' not found, defaulting to 'moyen terme'.")
                urgency_orm = self._session.query(LeadUrgencyORM).filter_by(name='moyen terme').first()

            urgency = LeadUrgency(
                id=urgency_orm.id,
                name=urgency_orm.name
            ) if urgency_orm else None

            # Get status
            status_orm = self._session.query(LeadStatusORM).filter_by(name='nouveau').first()
            if not status_orm:
                logger.error("Default lead status 'nouveau' not found in the database.")
                raise ValueError("Initial lead status 'nouveau' is not configured in the system.")

            status = LeadStatus(
                id=status_orm.id,
                name=status_orm.name
            )

            # Get positions and concerns
            positions = [self._get_or_create_position(title) for title in lead_payload.positions]
            concerns = [self._get_or_create_concern(label) for label in lead_payload.concerns]

            # Create lead domain entity
            lead = Lead(
                id=None,
                submission_date=datetime.now(),
                estimated_users=lead_payload.estimated_users,
                problem_summary=lead_payload.problem_summary,
                maturity_score=maturity_score,
                altcha_solution=altcha,
                fingerprint_visitor_id=visitor_id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                contact=contact,
                company=company,
                status=status,
                urgency=urgency,
                recommended_pack=recommended_pack,
                positions=positions,
                concerns=concerns
            )

            # Save lead via repository
            saved_lead = self._lead_repo.save(lead)

            # Create LeadPosition and LeadConcern associations (still ORM-based)
            for position in positions:
                lead_position = LeadPosition(lead_id=saved_lead.id, position_id=position.id)
                self._session.add(lead_position)

            for concern in concerns:
                lead_concern = LeadConcern(lead_id=saved_lead.id, concern_id=concern.id)
                self._session.add(lead_concern)

            self._session.commit()

            # Return ORM model for API compatibility
            lead_orm = self._session.query(LeadORM).filter(LeadORM.id == saved_lead.id).first()
            return lead_orm

        except Exception as e:
            logger.exception("Error creating lead")
            raise e

    def get_all_leads(self) -> List[LeadORM]:
        """Get all leads - returns ORM models for API compatibility."""
        try:
            leads = self._lead_repo.find_all()
            # Convert back to ORM for API compatibility
            lead_ids = [lead.id for lead in leads]
            return self._session.query(LeadORM).filter(LeadORM.id.in_(lead_ids)).all()
        except Exception as e:
            logger.exception("Error getting all leads")
            raise e

    def get_lead_by_id(self, lead_id: int) -> Optional[LeadORM]:
        """Get lead by ID - returns ORM model for API compatibility."""
        try:
            lead = self._lead_repo.find_by_id(lead_id)
            if not lead:
                return None
            # Convert back to ORM for API compatibility
            return self._session.query(LeadORM).filter(LeadORM.id == lead.id).first()
        except Exception as e:
            logger.exception(f"Error getting lead by id {lead_id}")
            raise e

    def update_lead_notes(self, lead_id: int, notes: str) -> LeadORM:
        """Update lead notes - returns ORM model for API compatibility."""
        try:
            lead_orm = self._session.query(LeadORM).filter(LeadORM.id == lead_id).one_or_none()
            if lead_orm:
                # Get or create a "note interne" reason for internal notes
                reason = self._note_repo.find_reason_by_name("note interne")
                if not reason:
                    # Fallback to first available reason
                    reasons = self._note_repo.get_all_reasons()
                    if reasons:
                        reason = reasons[0]
                    else:
                        # Create default reason (still ORM-based for now)
                        from infrastructure.persistence.models import NoteReasonModel as NoteReasonORM
                        reason_orm = NoteReasonORM(name="note interne")
                        self._session.add(reason_orm)
                        self._session.commit()
                        self._session.refresh(reason_orm)
                        reason = NoteReason(id=reason_orm.id, name=reason_orm.name)

                # Create note domain entity
                note = Note(
                    id=None,
                    note=notes,
                    created_at=datetime.now(),
                    author_name="system",
                    lead_id=lead_id,
                    reason=reason
                )
                self._note_repo.save(note)

                self._session.refresh(lead_orm)

            return lead_orm
        except Exception as e:
            logger.exception(f"Error updating notes for lead {lead_id}")
            raise e

    def update_lead(self, lead_id: int, lead_update: LeadUpdateRequest) -> Optional[LeadORM]:
        """Update lead - returns ORM model for API compatibility."""
        lead_orm = self.get_lead_by_id(lead_id)
        if not lead_orm:
            return None

        if lead_orm.fingerprint_visitor_id != lead_update.visitorId or lead_orm.altcha_solution != lead_update.altcha:
            raise ValueError("Fingerprint or Altcha solution does not match.")

        for field, value in lead_update.model_dump(exclude_unset=True).items():
            if field in ["altcha", "visitorId"]:
                continue

            # Handle related fields
            if field in ["name", "email", "phone", "job_title", "conscent"]:
                old_value = getattr(lead_orm.contact, field)
                if old_value != value:
                    log_entry = LeadModificationLog(
                        lead_id=lead_id, field_name=field, old_value=str(old_value), new_value=str(value)
                    )
                    self._session.add(log_entry)
                    setattr(lead_orm.contact, field, value)
            elif field in ["company_name", "company_size"]:
                if field == "company_name":
                    old_value = lead_orm.company.name
                    if old_value != value:
                        log_entry = LeadModificationLog(
                            lead_id=lead_id, field_name=field, old_value=str(old_value), new_value=str(value)
                        )
                        self._session.add(log_entry)
                        lead_orm.company.name = value
                else:  # company_size
                    old_value = lead_orm.company.size
                    if old_value != value:
                        log_entry = LeadModificationLog(
                            lead_id=lead_id, field_name=field, old_value=str(old_value), new_value=str(value)
                        )
                        self._session.add(log_entry)
                        lead_orm.company.size = value
            elif field == "positions":
                # For simplicity, we replace all positions
                old_positions = [p.title for p in lead_orm.positions]
                log_entry = LeadModificationLog(
                    lead_id=lead_id, field_name=field, old_value=str(old_positions), new_value=str(value)
                )
                self._session.add(log_entry)

                self._session.query(LeadPosition).filter_by(lead_id=lead_orm.id).delete()
                for position_title in value:
                    position = self._get_or_create_position(position_title)
                    lead_position = LeadPosition(lead_id=lead_orm.id, position_id=position.id)
                    self._session.add(lead_position)
            elif field == "concerns":
                # For simplicity, we replace all concerns
                old_concerns = [c.label for c in lead_orm.concerns]
                log_entry = LeadModificationLog(
                    lead_id=lead_id, field_name=field, old_value=str(old_concerns), new_value=str(value)
                )
                self._session.add(log_entry)

                self._session.query(LeadConcern).filter_by(lead_id=lead_orm.id).delete()
                for concern_label in value:
                    concern = self._get_or_create_concern(concern_label)
                    lead_concern = LeadConcern(lead_id=lead_orm.id, concern_id=concern.id)
                    self._session.add(lead_concern)
            elif field == "urgency":
                # Handle urgency by looking up the LeadUrgency enum
                urgency = self._session.query(LeadUrgencyORM).filter_by(name=value).one_or_none()
                if not urgency:
                    raise ValueError(f"Invalid urgency value: {value}")
                old_value = lead_orm.urgency.name if lead_orm.urgency else None
                if old_value != value:
                    log_entry = LeadModificationLog(
                        lead_id=lead_id, field_name=field, old_value=str(old_value), new_value=str(value)
                    )
                    self._session.add(log_entry)
                    lead_orm.urgency_id = urgency.id
            else:
                old_value = getattr(lead_orm, field)
                if old_value != value:
                    log_entry = LeadModificationLog(
                        lead_id=lead_id, field_name=field, old_value=str(old_value), new_value=str(value)
                    )
                    self._session.add(log_entry)
                    setattr(lead_orm, field, value)

        self._session.commit()
        self._session.refresh(lead_orm)
        return lead_orm
