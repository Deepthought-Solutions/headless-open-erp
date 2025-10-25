import pytest
from unittest.mock import MagicMock
from datetime import datetime
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from application.email_service import EmailAccountService, ClassifiedEmailService
from domain.orm import EmailAccount, ClassifiedEmail, EmailClassificationHistory
from domain.contact import (
    EmailAccountCreate, EmailAccountUpdate,
    ClassifiedEmailCreate, ClassifiedEmailUpdate
)


@pytest.fixture
def db_session():
    return MagicMock()


@pytest.fixture
def email_account_service(db_session):
    return EmailAccountService(db_session)


@pytest.fixture
def classified_email_service(db_session):
    return ClassifiedEmailService(db_session)


# EmailAccountService Tests
def test_create_account_success(email_account_service, db_session):
    account_data = EmailAccountCreate(
        name="Test Account",
        imap_host="imap.example.com",
        imap_port=993,
        imap_username="user@example.com",
        imap_password="password123",
        imap_use_ssl=True
    )

    account = email_account_service.create_account(account_data)

    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once()


def test_create_account_with_ssl_false(email_account_service, db_session):
    account_data = EmailAccountCreate(
        name="Test Account No SSL",
        imap_host="imap.example.com",
        imap_port=143,
        imap_username="user@example.com",
        imap_password="password123",
        imap_use_ssl=False
    )

    account = email_account_service.create_account(account_data)

    db_session.add.assert_called_once()
    # Verify that the account was created with imap_use_ssl=0 (SQLite compatible)
    added_account = db_session.add.call_args[0][0]
    assert added_account.imap_use_ssl == 0


def test_get_account_by_id(email_account_service, db_session):
    mock_account = EmailAccount(
        id=1,
        name="Test Account",
        imap_host="imap.example.com",
        imap_port=993,
        imap_username="user@example.com",
        imap_password="password123",
        imap_use_ssl=1
    )
    db_session.query.return_value.filter.return_value.first.return_value = mock_account

    account = email_account_service.get_account_by_id(1)

    assert account.name == "Test Account"
    db_session.query.assert_called_once()


def test_get_all_accounts(email_account_service, db_session):
    db_session.query.return_value.all.return_value = [
        EmailAccount(id=1, name="Account 1"),
        EmailAccount(id=2, name="Account 2")
    ]

    accounts = email_account_service.get_all_accounts()

    assert len(accounts) == 2
    db_session.query.assert_called_once()


def test_update_account_success(email_account_service, db_session):
    mock_account = EmailAccount(
        id=1,
        name="Old Name",
        imap_host="old.example.com",
        imap_port=993,
        imap_username="user@example.com",
        imap_password="password123",
        imap_use_ssl=1
    )
    db_session.query.return_value.filter.return_value.first.return_value = mock_account

    update_data = EmailAccountUpdate(
        name="New Name",
        imap_host="new.example.com"
    )

    account = email_account_service.update_account(1, update_data)

    assert account.name == "New Name"
    assert account.imap_host == "new.example.com"
    db_session.commit.assert_called_once()


def test_update_account_not_found(email_account_service, db_session):
    db_session.query.return_value.filter.return_value.first.return_value = None

    update_data = EmailAccountUpdate(name="New Name")
    account = email_account_service.update_account(999, update_data)

    assert account is None


def test_delete_account_success(email_account_service, db_session):
    mock_account = EmailAccount(id=1, name="Test Account")
    db_session.query.return_value.filter.return_value.first.return_value = mock_account

    success = email_account_service.delete_account(1)

    assert success is True
    db_session.delete.assert_called_once_with(mock_account)
    db_session.commit.assert_called_once()


def test_delete_account_not_found(email_account_service, db_session):
    db_session.query.return_value.filter.return_value.first.return_value = None

    success = email_account_service.delete_account(999)

    assert success is False


# ClassifiedEmailService Tests
def test_create_classified_email_success(classified_email_service, db_session):
    email_data = ClassifiedEmailCreate(
        email_account_id=1,
        imap_id="12345",
        sender="sender@example.com",
        recipients="recipient1@example.com,recipient2@example.com",
        subject="Test Email",
        email_date=datetime.now(),
        classification="sales_inquiry",
        emergency_level=3,
        abstract="This is a test abstract",
        lead_id=None
    )

    db_session.query.return_value.filter.return_value.first.return_value = None

    email = classified_email_service.create_classified_email(email_data)

    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once()


def test_create_classified_email_invalid_emergency_level(classified_email_service, db_session):
    email_data = ClassifiedEmailCreate(
        email_account_id=1,
        imap_id="12345",
        sender="sender@example.com",
        recipients="recipient@example.com",
        emergency_level=6  # Invalid: must be 1-5
    )

    with pytest.raises(ValueError, match="Emergency level must be between 1 and 5"):
        classified_email_service.create_classified_email(email_data)


def test_create_classified_email_abstract_too_long(classified_email_service, db_session):
    email_data = ClassifiedEmailCreate(
        email_account_id=1,
        imap_id="12345",
        sender="sender@example.com",
        recipients="recipient@example.com",
        abstract="x" * 201  # Invalid: must be 200 chars or less
    )

    with pytest.raises(ValueError, match="Abstract must be 200 characters or less"):
        classified_email_service.create_classified_email(email_data)


def test_create_classified_email_duplicate(classified_email_service, db_session):
    email_data = ClassifiedEmailCreate(
        email_account_id=1,
        imap_id="12345",
        sender="sender@example.com",
        recipients="recipient@example.com"
    )

    # Simulate existing email
    mock_existing = ClassifiedEmail(id=1, email_account_id=1, imap_id="12345")
    db_session.query.return_value.filter.return_value.first.return_value = mock_existing

    with pytest.raises(ValueError, match="Email with this IMAP ID already exists"):
        classified_email_service.create_classified_email(email_data)


def test_get_email_by_id(classified_email_service, db_session):
    mock_email = ClassifiedEmail(
        id=1,
        email_account_id=1,
        imap_id="12345",
        sender="sender@example.com",
        recipients="recipient@example.com"
    )
    db_session.query.return_value.options.return_value.filter.return_value.first.return_value = mock_email

    email = classified_email_service.get_email_by_id(1)

    assert email.imap_id == "12345"
    db_session.query.assert_called_once()


def test_get_email_by_imap_id(classified_email_service, db_session):
    mock_email = ClassifiedEmail(
        id=1,
        email_account_id=1,
        imap_id="12345",
        sender="sender@example.com",
        recipients="recipient@example.com"
    )
    db_session.query.return_value.filter.return_value.first.return_value = mock_email

    email = classified_email_service.get_email_by_imap_id(1, "12345")

    assert email.id == 1
    db_session.query.assert_called_once()


def test_get_all_emails_no_filters(classified_email_service, db_session):
    db_session.query.return_value.order_by.return_value.all.return_value = [
        ClassifiedEmail(id=1),
        ClassifiedEmail(id=2)
    ]

    emails = classified_email_service.get_all_emails()

    assert len(emails) == 2


def test_get_all_emails_with_filters(classified_email_service, db_session):
    mock_query = MagicMock()
    db_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_query
    mock_query.order_by.return_value.all.return_value = [ClassifiedEmail(id=1)]

    emails = classified_email_service.get_all_emails(
        email_account_id=1,
        emergency_level=5,
        classification="urgent",
        lead_id=10
    )

    # Verify filters were applied (4 filters)
    assert mock_query.filter.call_count == 4


def test_update_classification_success(classified_email_service, db_session):
    mock_email = ClassifiedEmail(
        id=1,
        classification="old_classification",
        emergency_level=2,
        abstract="old abstract"
    )
    mock_email.classification_history = []

    db_session.query.return_value.options.return_value.filter.return_value.first.return_value = mock_email

    update_data = ClassifiedEmailUpdate(
        classification="new_classification",
        emergency_level=4,
        abstract="new abstract",
        change_reason="LLM re-evaluated"
    )

    email = classified_email_service.update_classification(1, update_data)

    # Verify history was created
    db_session.add.assert_called_once()
    added_history = db_session.add.call_args[0][0]
    assert isinstance(added_history, EmailClassificationHistory)
    assert added_history.classification == "old_classification"
    assert added_history.change_reason == "LLM re-evaluated"

    # Verify email was updated
    assert mock_email.classification == "new_classification"
    assert mock_email.emergency_level == 4
    assert mock_email.abstract == "new abstract"


def test_update_classification_not_found(classified_email_service, db_session):
    db_session.query.return_value.options.return_value.filter.return_value.first.return_value = None

    update_data = ClassifiedEmailUpdate(classification="new")
    email = classified_email_service.update_classification(999, update_data)

    assert email is None


def test_update_classification_invalid_emergency_level(classified_email_service, db_session):
    mock_email = ClassifiedEmail(id=1)
    db_session.query.return_value.options.return_value.filter.return_value.first.return_value = mock_email

    update_data = ClassifiedEmailUpdate(emergency_level=0)

    with pytest.raises(ValueError, match="Emergency level must be between 1 and 5"):
        classified_email_service.update_classification(1, update_data)


def test_delete_email_success(classified_email_service, db_session):
    mock_email = ClassifiedEmail(id=1)
    db_session.query.return_value.options.return_value.filter.return_value.first.return_value = mock_email

    success = classified_email_service.delete_email(1)

    assert success is True
    db_session.delete.assert_called_once_with(mock_email)
    db_session.commit.assert_called_once()


def test_delete_email_not_found(classified_email_service, db_session):
    db_session.query.return_value.options.return_value.filter.return_value.first.return_value = None

    success = classified_email_service.delete_email(999)

    assert success is False
