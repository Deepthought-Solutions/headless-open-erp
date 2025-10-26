import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from application.note_service import NoteService
from domain.orm import Lead, Note, NoteReason, Contact
from domain.contact import NoteCreateRequest

@pytest.fixture
def note_repository():
    return MagicMock()

@pytest.fixture
def email_notification_service():
    return MagicMock()

@pytest.fixture
def note_service(note_repository, email_notification_service):
    return NoteService(note_repository, email_notification_service)

def test_create_note_success(note_service, note_repository, email_notification_service):
    from domain.entities.note import NoteReason as NoteReasonEntity, Note as NoteEntity
    from infrastructure.persistence.models import LeadModel, ContactModel

    # Create a lead model with contact
    contact = ContactModel(email="test@example.com")
    lead = LeadModel(id=1, contact=contact)

    note_request = NoteCreateRequest(note="Test note", reason="appel sortant")
    author_name = "testuser"

    # Mock repository to return reason
    reason_entity = NoteReasonEntity(id=1, name="appel sortant")
    note_repository.find_reason_by_name.return_value = reason_entity

    # Mock save to return saved note
    saved_note = NoteEntity(
        id=1,
        note="Test note",
        created_at=datetime.now(),
        author_name="testuser",
        lead_id=1,
        reason=reason_entity
    )
    note_repository.save.return_value = saved_note

    note = note_service.create_note(lead, note_request, author_name)

    assert note.note == "Test note"
    assert note.author_name == "testuser"
    note_repository.save.assert_called_once()
    email_notification_service.send_note_notification.assert_not_called()

def test_create_note_with_email(note_service, note_repository, email_notification_service):
    from domain.entities.note import NoteReason as NoteReasonEntity, Note as NoteEntity
    from infrastructure.persistence.models import LeadModel, ContactModel

    # Create a lead model with contact
    contact = ContactModel(email="test@example.com")
    lead = LeadModel(id=1, contact=contact)

    note_request = NoteCreateRequest(
        note="Test note",
        reason="appel sortant",
        send_to_contact=True,
        send_to_recipients=["another@example.com"]
    )
    author_name = "testuser"

    # Mock repository to return reason
    reason_entity = NoteReasonEntity(id=1, name="appel sortant")
    note_repository.find_reason_by_name.return_value = reason_entity

    # Mock save to return saved note
    saved_note = NoteEntity(
        id=1,
        note="Test note",
        created_at=datetime.now(),
        author_name="testuser",
        lead_id=1,
        reason=reason_entity
    )
    note_repository.save.return_value = saved_note

    note_service.create_note(lead, note_request, author_name)

    email_notification_service.send_note_notification.assert_called_once()
    _, kwargs = email_notification_service.send_note_notification.call_args
    assert "note" in kwargs and kwargs["note"] == "Test note"
    assert "author" in kwargs and kwargs["author"] == "testuser"
    assert "recipients" in kwargs and set(kwargs["recipients"]) == {"test@example.com", "another@example.com"}

def test_get_notes_by_lead_id(note_service, note_repository):
    from domain.entities.note import Note as NoteEntity, NoteReason as NoteReasonEntity

    # Mock repository to return notes
    reason = NoteReasonEntity(id=1, name="appel sortant")
    mock_notes = [
        NoteEntity(id=1, note="Note 1", created_at=datetime.now(), author_name="user1", lead_id=1, reason=reason),
        NoteEntity(id=2, note="Note 2", created_at=datetime.now(), author_name="user2", lead_id=1, reason=reason)
    ]
    note_repository.find_by_lead_id.return_value = mock_notes

    notes = note_service.get_notes_by_lead_id(1)

    assert len(notes) == 2
    note_repository.find_by_lead_id.assert_called_once_with(1)
