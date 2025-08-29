import pytest
from unittest.mock import MagicMock, patch
from application.note_service import NoteService
from domain.orm import Lead, Note, NoteReason, Contact
from domain.contact import NoteCreateRequest

@pytest.fixture
def db_session():
    return MagicMock()

@pytest.fixture
def email_service():
    return MagicMock()

@pytest.fixture
def note_service(db_session, email_service):
    return NoteService(db_session, email_service)

def test_create_note_success(note_service, db_session, email_service):
    lead = Lead(id=1, contact=Contact(email="test@example.com"))
    note_request = NoteCreateRequest(note="Test note", reason="appel sortant")
    author_name = "testuser"

    db_session.query.return_value.filter_by.return_value.first.return_value = NoteReason(id=1, name="appel sortant")

    note = note_service.create_note(lead, note_request, author_name)

    assert note.note == "Test note"
    assert note.author_name == "testuser"
    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once()
    email_service.send_note_notification.assert_not_called()

def test_create_note_with_email(note_service, db_session, email_service):
    lead = Lead(id=1, contact=Contact(email="test@example.com"))
    note_request = NoteCreateRequest(
        note="Test note",
        reason="appel sortant",
        send_to_contact=True,
        send_to_recipients=["another@example.com"]
    )
    author_name = "testuser"

    db_session.query.return_value.filter_by.return_value.first.return_value = NoteReason(id=1, name="appel sortant")

    note_service.create_note(lead, note_request, author_name)

    email_service.send_note_notification.assert_called_once()
    _, kwargs = email_service.send_note_notification.call_args
    assert "note" in kwargs and kwargs["note"] == "Test note"
    assert "author" in kwargs and kwargs["author"] == "testuser"
    assert "recipients" in kwargs and set(kwargs["recipients"]) == {"test@example.com", "another@example.com"}

def test_get_notes_by_lead_id(note_service, db_session):
    note_service.get_notes_by_lead_id(1)
    db_session.query.assert_called_once()
