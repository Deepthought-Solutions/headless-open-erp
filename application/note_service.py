import logging
from sqlalchemy.orm import Session, joinedload
from domain.orm import Note, NoteReason, Lead
from domain.contact import NoteCreateRequest
from application.notification_service import EmailNotificationService

logger = logging.getLogger(__name__)

class NoteService:
    def __init__(self, db: Session, email_notification_service: EmailNotificationService):
        self.db = db
        self.email_notification_service = email_notification_service

    def create_note(self, lead: Lead, note_create_request: NoteCreateRequest, author_name: str) -> Note:
        try:
            reason = self.db.query(NoteReason).filter_by(name=note_create_request.reason).first()
            if not reason:
                raise ValueError(f"Reason '{note_create_request.reason}' not found")

            note = Note(
                note=note_create_request.note,
                author_name=author_name,
                lead_id=lead.id,
                reason_id=reason.id
            )
            self.db.add(note)
            self.db.commit()
            self.db.refresh(note)

            recipients = []
            if note_create_request.send_to_contact:
                recipients.append(lead.contact.email)

            if note_create_request.send_to_recipients:
                recipients.extend(note_create_request.send_to_recipients)

            if recipients:
                self.email_notification_service.send_note_notification(
                    recipients=list(set(recipients)),
                    note=note.note,
                    author=author_name
                )

            return note
        except Exception as e:
            logger.exception("Error creating note")
            raise e

    def get_notes_by_lead_id(self, lead_id: int) -> list[Note]:
        try:
            return self.db.query(Note).options(
                joinedload(Note.reason)
            ).filter(Note.lead_id == lead_id).order_by(Note.created_at.desc()).all()
        except Exception as e:
            logger.exception(f"Error getting notes for lead {lead_id}")
            raise e
