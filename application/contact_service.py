import logging, sys
from sqlalchemy.orm import Session, joinedload
from domain.orm import Company, Position, Concern, Contact, Lead, LeadPosition, LeadConcern, RecommendedPack, LeadUrgency, LeadStatus, LeadModificationLog, Note, NoteReason
from domain.contact import LeadPayload, LeadUpdateRequest

logger = logging.getLogger(__name__)
# Configure logging
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.handlers = []  # Nettoie les handlers existants
logger.addHandler(handler)

logger.propagate = False


class LeadService:
    def __init__(self, db: Session):
        self.db = db

    def _get_or_create_contact(self, name: str, email: str, phone: str, job_title: str, conscent: bool = False) -> Contact:
        contact = self.db.query(Contact).filter_by(email=email).first()
        if not contact:
            contact = Contact(name=name, email=email, phone=phone, job_title=job_title, conscent=conscent)
            self.db.add(contact)
            self.db.commit()
            self.db.refresh(contact)
        else:
            # Update contact info if it has changed
            contact.name = name
            contact.phone = phone
            contact.job_title = job_title
            contact.conscent = conscent
            self.db.commit()
            self.db.refresh(contact)
        return contact

    def _get_or_create_company(self, company_name: str, size: int) -> Company:
        company = self.db.query(Company).filter_by(name=company_name).first()
        if not company:
            company = Company(name=company_name, size=size)
            self.db.add(company)
            self.db.commit()
            self.db.refresh(company)
        else:
            company.size = size
            self.db.commit()
            self.db.refresh(company)
        return company

    def _get_or_create_position(self, position_title: str) -> Position:
        position = self.db.query(Position).filter_by(title=position_title).first()
        if not position:
            position = Position(title=position_title)
            self.db.add(position)
            self.db.commit()
            self.db.refresh(position)
        return position

    def _get_or_create_concern(self, concern_label: str) -> Concern:
        concern = self.db.query(Concern).filter_by(label=concern_label).first()
        if not concern:
            concern = Concern(label=concern_label)
            self.db.add(concern)
            self.db.commit()
            self.db.refresh(concern)
        return concern

    def _calculate_maturity_score(self, payload: LeadPayload) -> int:
        score = 0
        if payload.company_size and payload.company_size > 100:
            score += 1
        if payload.estimated_users and payload.estimated_users > 50:
            score += 1
        if len(payload.concerns) > 2:
            score += 1
        if payload.job_title and any(role in payload.job_title.lower() for role in ['manager', 'director', 'cto', 'ceo']):
            score += 1

        return min(score, 5)

    def _recommend_pack(self, payload: LeadPayload) -> RecommendedPack:
        pack_name = "conformité"
        if any("confiance" in c.lower() for c in payload.concerns):
            pack_name = "confiance"
        elif any("croissance" in c.lower() for c in payload.concerns):
            pack_name = "croissance"

        pack = self.db.query(RecommendedPack).filter_by(name=pack_name).first()
        if not pack:
            logger.error(f"Recommended pack '{pack_name}' not found in the database.")
            pack = self.db.query(RecommendedPack).filter_by(name='conformité').first()
        return pack

    def create_lead(self, lead_payload: LeadPayload, altcha: str, visitor_id: str) -> Lead:
        try:
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

            maturity_score = self._calculate_maturity_score(lead_payload)
            recommended_pack = self._recommend_pack(lead_payload)
            urgency = self.db.query(LeadUrgency).filter_by(name=lead_payload.urgency).first()
            if not urgency:
                logger.warning(f"Urgency '{lead_payload.urgency}' not found, defaulting to 'moyen terme'.")
                urgency = self.db.query(LeadUrgency).filter_by(name='moyen terme').first()

            status = self.db.query(LeadStatus).filter_by(name='nouveau').first()
            if not status:
                logger.error("Default lead status 'nouveau' not found in the database.")
                raise ValueError("Initial lead status 'nouveau' is not configured in the system.")


            lead = Lead(
                contact_id=contact.id,
                company_id=company.id,
                problem_summary=lead_payload.problem_summary,
                estimated_users=lead_payload.estimated_users,
                urgency_id=urgency.id,
                status_id=status.id,
                maturity_score=maturity_score,
                recommended_pack_id=recommended_pack.id,
                altcha_solution=altcha,
                fingerprint_visitor_id=visitor_id,
            )
            self.db.add(lead)
            self.db.commit()
            self.db.refresh(lead)

            for position_title in lead_payload.positions:
                position = self._get_or_create_position(position_title)
                lead_position = LeadPosition(lead_id=lead.id, position_id=position.id)
                self.db.add(lead_position)

            for concern_label in lead_payload.concerns:
                concern = self._get_or_create_concern(concern_label)
                lead_concern = LeadConcern(lead_id=lead.id, concern_id=concern.id)
                self.db.add(lead_concern)

            self.db.commit()

            return lead
        except Exception as e:
            logger.exception("Error creating lead")
            raise e

    def get_all_leads(self) -> list[Lead]:
        try:
            return self.db.query(Lead).options(
                joinedload(Lead.contact),
                joinedload(Lead.company),
                joinedload(Lead.status),
                joinedload(Lead.urgency),
                joinedload(Lead.recommended_pack),
                joinedload(Lead.positions),
                joinedload(Lead.concerns)
            ).all()
        except Exception as e:
            logger.exception("Error getting all leads")
            raise e

    def get_lead_by_id(self, lead_id: int) -> Lead:
        try:
            lead = self.db.query(Lead).options(
                joinedload(Lead.contact),
                joinedload(Lead.company),
                joinedload(Lead.status),
                joinedload(Lead.urgency),
                joinedload(Lead.recommended_pack),
                joinedload(Lead.positions),
                joinedload(Lead.concerns)
            ).filter(Lead.id == lead_id).one_or_none()
            return lead
        except Exception as e:
            logger.exception(f"Error getting lead by id {lead_id}")
            raise e

    def update_lead_notes(self, lead_id: int, notes: str) -> Lead:
        try:
            lead = self.db.query(Lead).filter(Lead.id == lead_id).one_or_none()
            if lead:
                # Get or create a "note interne" reason for internal notes
                reason = self.db.query(NoteReason).filter_by(name="note interne").one_or_none()
                if not reason:
                    # If it doesn't exist, use any available reason or create a default
                    reason = self.db.query(NoteReason).first()
                    if not reason:
                        reason = NoteReason(name="note interne")
                        self.db.add(reason)
                        self.db.commit()
                        self.db.refresh(reason)

                # Create a new Note record
                note = Note(
                    note=notes,
                    author_name="system",  # Default author for internal notes
                    lead_id=lead_id,
                    reason_id=reason.id
                )
                self.db.add(note)
                self.db.commit()
                self.db.refresh(lead)
            return lead
        except Exception as e:
            logger.exception(f"Error updating notes for lead {lead_id}")
            raise e

    def update_lead(self, lead_id: int, lead_update: "LeadUpdateRequest") -> Lead:
        lead = self.get_lead_by_id(lead_id)
        if not lead:
            return None

        if lead.fingerprint_visitor_id != lead_update.visitorId or lead.altcha_solution != lead_update.altcha:
            raise ValueError("Fingerprint or Altcha solution does not match.")

        for field, value in lead_update.model_dump(exclude_unset=True).items():
            if field in ["altcha", "visitorId"]:
                continue

            # Handle related fields
            if field in ["name", "email", "phone", "job_title", "conscent"]:
                old_value = getattr(lead.contact, field)
                if old_value != value:
                    log_entry = LeadModificationLog(
                        lead_id=lead_id, field_name=field, old_value=str(old_value), new_value=str(value)
                    )
                    self.db.add(log_entry)
                    setattr(lead.contact, field, value)
            elif field in ["company_name", "company_size"]:
                if field == "company_name":
                    old_value = lead.company.name
                    if old_value != value:
                        log_entry = LeadModificationLog(
                            lead_id=lead_id, field_name=field, old_value=str(old_value), new_value=str(value)
                        )
                        self.db.add(log_entry)
                        lead.company.name = value
                else: # company_size
                    old_value = lead.company.size
                    if old_value != value:
                        log_entry = LeadModificationLog(
                            lead_id=lead_id, field_name=field, old_value=str(old_value), new_value=str(value)
                        )
                        self.db.add(log_entry)
                        lead.company.size = value
            elif field == "positions":
                # For simplicity, we replace all positions
                old_positions = [p.title for p in lead.positions]
                log_entry = LeadModificationLog(
                    lead_id=lead_id, field_name=field, old_value=str(old_positions), new_value=str(value)
                )
                self.db.add(log_entry)

                self.db.query(LeadPosition).filter_by(lead_id=lead.id).delete()
                for position_title in value:
                    position = self._get_or_create_position(position_title)
                    lead_position = LeadPosition(lead_id=lead.id, position_id=position.id)
                    self.db.add(lead_position)
            elif field == "concerns":
                # For simplicity, we replace all concerns
                old_concerns = [c.label for c in lead.concerns]
                log_entry = LeadModificationLog(
                    lead_id=lead_id, field_name=field, old_value=str(old_concerns), new_value=str(value)
                )
                self.db.add(log_entry)

                self.db.query(LeadConcern).filter_by(lead_id=lead.id).delete()
                for concern_label in value:
                    concern = self._get_or_create_concern(concern_label)
                    lead_concern = LeadConcern(lead_id=lead.id, concern_id=concern.id)
                    self.db.add(lead_concern)
            elif field == "urgency":
                # Handle urgency by looking up the LeadUrgency enum
                urgency = self.db.query(LeadUrgency).filter_by(name=value).one_or_none()
                if not urgency:
                    raise ValueError(f"Invalid urgency value: {value}")
                old_value = lead.urgency.name if lead.urgency else None
                if old_value != value:
                    log_entry = LeadModificationLog(
                        lead_id=lead_id, field_name=field, old_value=str(old_value), new_value=str(value)
                    )
                    self.db.add(log_entry)
                    lead.urgency_id = urgency.id
            else:
                old_value = getattr(lead, field)
                if old_value != value:
                    log_entry = LeadModificationLog(
                        lead_id=lead_id, field_name=field, old_value=str(old_value), new_value=str(value)
                    )
                    self.db.add(log_entry)
                    setattr(lead, field, value)

        self.db.commit()
        self.db.refresh(lead)
        return lead
