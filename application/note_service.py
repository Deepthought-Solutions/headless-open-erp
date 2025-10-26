import logging
from datetime import datetime

from domain.repositories.note_repository import NoteRepository
from domain.entities.note import Note
from domain.contact import NoteCreateRequest
from application.notification_service import EmailNotificationService
# Still need access to Lead ORM for email notification until we migrate it
from infrastructure.persistence.models import LeadModel as Lead

logger = logging.getLogger(__name__)

class NoteService:
    """Application service for note operations - uses repository pattern."""

    def __init__(self, note_repository: NoteRepository, email_notification_service: EmailNotificationService):
        self._note_repo = note_repository
        self.email_notification_service = email_notification_service

    def create_note(self, lead: Lead, note_create_request: NoteCreateRequest, author_name: str) -> Note:
        """Create a note for a lead."""
        try:
            # Find reason
            reason = self._note_repo.find_reason_by_name(note_create_request.reason)
            if not reason:
                raise ValueError(f"Reason '{note_create_request.reason}' not found")

            # Create note domain entity
            note = Note(
                id=None,
                note=note_create_request.note,
                created_at=datetime.now(),
                author_name=author_name,
                lead_id=lead.id,
                reason=reason
            )

            # Save via repository
            saved_note = self._note_repo.save(note)

            # Send email notifications if requested
            recipients = []
            if note_create_request.send_to_contact:
                recipients.append(lead.contact.email)

            if note_create_request.send_to_recipients:
                recipients.extend(note_create_request.send_to_recipients)

            if recipients:
                self.email_notification_service.send_note_notification(
                    recipients=list(set(recipients)),
                    note=saved_note.note,
                    author=author_name
                )

            return saved_note
        except Exception as e:
            logger.exception("Error creating note")
            raise e

    def get_notes_by_lead_id(self, lead_id: int) -> list[Note]:
        """Get all notes for a lead."""
        try:
            return self._note_repo.find_by_lead_id(lead_id)
        except Exception as e:
            logger.exception(f"Error getting notes for lead {lead_id}")
            raise e
