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
def email_account_repository():
    return MagicMock()


@pytest.fixture
def classified_email_repository():
    return MagicMock()


@pytest.fixture
def email_account_service(email_account_repository):
    return EmailAccountService(email_account_repository)


@pytest.fixture
def classified_email_service(db_session, classified_email_repository):
    return ClassifiedEmailService(db_session, classified_email_repository)


# EmailAccountService Tests
def test_create_account_success(email_account_service, email_account_repository):
    from domain.entities.email import EmailAccount as EmailAccountEntity
    from infrastructure.persistence.models import EmailAccountModel

    account_data = EmailAccountCreate(
        name="Test Account",
        imap_host="imap.example.com",
        imap_port=993,
        imap_username="user@example.com",
        imap_password="password123",
        imap_use_ssl=True
    )

    mock_entity = EmailAccountEntity(
        id=1,
        name="Test Account",
        imap_host="imap.example.com",
        imap_port=993,
        imap_username="user@example.com",
        imap_password="password123",
        imap_use_ssl=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    email_account_repository.save.return_value = mock_entity

    account = email_account_service.create_account(account_data)

    email_account_repository.save.assert_called_once()
    assert isinstance(account, EmailAccountModel)


def test_create_account_with_ssl_false(email_account_service, email_account_repository):
    from domain.entities.email import EmailAccount as EmailAccountEntity
    from infrastructure.persistence.models import EmailAccountModel

    account_data = EmailAccountCreate(
        name="Test Account No SSL",
        imap_host="imap.example.com",
        imap_port=143,
        imap_username="user@example.com",
        imap_password="password123",
        imap_use_ssl=False
    )

    mock_entity = EmailAccountEntity(
        id=1,
        name="Test Account No SSL",
        imap_host="imap.example.com",
        imap_port=143,
        imap_username="user@example.com",
        imap_password="password123",
        imap_use_ssl=False,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    email_account_repository.save.return_value = mock_entity

    account = email_account_service.create_account(account_data)

    email_account_repository.save.assert_called_once()
    # Verify that the account was created with imap_use_ssl=False
    saved_call = email_account_repository.save.call_args[0][0]
    assert saved_call.imap_use_ssl == False


def test_get_account_by_id(email_account_service, email_account_repository):
    from domain.entities.email import EmailAccount as EmailAccountEntity

    mock_entity = EmailAccountEntity(
        id=1,
        name="Test Account",
        imap_host="imap.example.com",
        imap_port=993,
        imap_username="user@example.com",
        imap_password="password123",
        imap_use_ssl=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    email_account_repository.find_by_id.return_value = mock_entity

    account = email_account_service.get_account_by_id(1)

    assert account.name == "Test Account"
    email_account_repository.find_by_id.assert_called_once_with(1)


def test_get_all_accounts(email_account_service, email_account_repository):
    from domain.entities.email import EmailAccount as EmailAccountEntity

    mock_entities = [
        EmailAccountEntity(id=1, name="Account 1", imap_host="host1", imap_port=993,
                          imap_username="user1", imap_password="pass1", imap_use_ssl=True,
                          created_at=datetime.now(), updated_at=datetime.now()),
        EmailAccountEntity(id=2, name="Account 2", imap_host="host2", imap_port=993,
                          imap_username="user2", imap_password="pass2", imap_use_ssl=True,
                          created_at=datetime.now(), updated_at=datetime.now())
    ]
    email_account_repository.find_all.return_value = mock_entities

    accounts = email_account_service.get_all_accounts()

    assert len(accounts) == 2
    email_account_repository.find_all.assert_called_once()


def test_update_account_success(email_account_service, email_account_repository):
    from domain.entities.email import EmailAccount as EmailAccountEntity

    mock_entity = EmailAccountEntity(
        id=1,
        name="Old Name",
        imap_host="old.example.com",
        imap_port=993,
        imap_username="user@example.com",
        imap_password="password123",
        imap_use_ssl=True,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    email_account_repository.find_by_id.return_value = mock_entity

    # Mock the update to modify the entity and return it
    def update_side_effect(entity):
        entity.name = "New Name"
        entity.imap_host = "new.example.com"
        return entity
    email_account_repository.update.side_effect = update_side_effect

    update_data = EmailAccountUpdate(
        name="New Name",
        imap_host="new.example.com"
    )

    account = email_account_service.update_account(1, update_data)

    assert account.name == "New Name"
    assert account.imap_host == "new.example.com"
    email_account_repository.update.assert_called_once()


def test_update_account_not_found(email_account_service, email_account_repository):
    email_account_repository.find_by_id.return_value = None

    update_data = EmailAccountUpdate(name="New Name")
    account = email_account_service.update_account(999, update_data)

    assert account is None


def test_delete_account_success(email_account_service, email_account_repository):
    from domain.entities.email import EmailAccount as EmailAccountEntity

    mock_entity = EmailAccountEntity(
        id=1, name="Test Account", imap_host="host", imap_port=993,
        imap_username="user", imap_password="pass", imap_use_ssl=True,
        created_at=datetime.now(), updated_at=datetime.now()
    )
    email_account_repository.find_by_id.return_value = mock_entity
    email_account_repository.delete.return_value = True

    success = email_account_service.delete_account(1)

    assert success is True
    email_account_repository.delete.assert_called_once_with(1)


def test_delete_account_not_found(email_account_service, email_account_repository):
    email_account_repository.find_by_id.return_value = None

    success = email_account_service.delete_account(999)

    assert success is False


# ClassifiedEmailService Tests
def test_create_classified_email_success(classified_email_service, classified_email_repository):
    from domain.entities.email import ClassifiedEmail as ClassifiedEmailEntity

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

    classified_email_repository.find_by_account_and_imap_id.return_value = None

    mock_entity = ClassifiedEmailEntity(
        id=1,
        email_account_id=1,
        imap_id="12345",
        sender="sender@example.com",
        recipients="recipient1@example.com,recipient2@example.com",
        subject="Test Email",
        email_date=datetime.now(),
        classification="sales_inquiry",
        emergency_level=3,
        abstract="This is a test abstract",
        lead_id=None,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    classified_email_repository.save.return_value = mock_entity

    email = classified_email_service.create_classified_email(email_data)

    classified_email_repository.save.assert_called_once()
    classified_email_repository.find_by_account_and_imap_id.assert_called_once_with(1, "12345")


def test_create_classified_email_invalid_emergency_level(classified_email_service, classified_email_repository):
    email_data = ClassifiedEmailCreate(
        email_account_id=1,
        imap_id="12345",
        sender="sender@example.com",
        recipients="recipient@example.com",
        emergency_level=6  # Invalid: must be 1-5
    )

    with pytest.raises(ValueError, match="Emergency level must be between 1 and 5"):
        classified_email_service.create_classified_email(email_data)


def test_create_classified_email_abstract_too_long(classified_email_service, classified_email_repository):
    email_data = ClassifiedEmailCreate(
        email_account_id=1,
        imap_id="12345",
        sender="sender@example.com",
        recipients="recipient@example.com",
        abstract="x" * 201  # Invalid: must be 200 chars or less
    )

    with pytest.raises(ValueError, match="Abstract must be 200 characters or less"):
        classified_email_service.create_classified_email(email_data)


def test_create_classified_email_duplicate(classified_email_service, classified_email_repository):
    from domain.entities.email import ClassifiedEmail as ClassifiedEmailEntity

    email_data = ClassifiedEmailCreate(
        email_account_id=1,
        imap_id="12345",
        sender="sender@example.com",
        recipients="recipient@example.com"
    )

    # Simulate existing email
    mock_existing = ClassifiedEmailEntity(
        id=1, email_account_id=1, imap_id="12345",
        sender="sender@example.com", recipients="recipient@example.com",
        subject=None, email_date=None, classification=None,
        emergency_level=None, abstract=None, lead_id=None,
        created_at=datetime.now(), updated_at=datetime.now()
    )
    classified_email_repository.find_by_account_and_imap_id.return_value = mock_existing

    with pytest.raises(ValueError, match="Email with this IMAP ID already exists"):
        classified_email_service.create_classified_email(email_data)


def test_get_email_by_id(classified_email_service, db_session):
    from infrastructure.persistence.models import ClassifiedEmailModel

    mock_email = ClassifiedEmailModel(
        id=1,
        email_account_id=1,
        imap_id="12345",
        sender="sender@example.com",
        recipients="recipient@example.com"
    )
    db_session.query.return_value.options.return_value.filter.return_value.one_or_none.return_value = mock_email

    email = classified_email_service.get_email_by_id(1)

    assert email.imap_id == "12345"
    db_session.query.assert_called_once()


def test_get_email_by_imap_id(classified_email_service, classified_email_repository):
    from domain.entities.email import ClassifiedEmail as ClassifiedEmailEntity

    mock_entity = ClassifiedEmailEntity(
        id=1,
        email_account_id=1,
        imap_id="12345",
        sender="sender@example.com",
        recipients="recipient@example.com",
        subject=None, email_date=None, classification=None,
        emergency_level=None, abstract=None, lead_id=None,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    classified_email_repository.find_by_account_and_imap_id.return_value = mock_entity

    email = classified_email_service.get_email_by_imap_id(1, "12345")

    assert email.id == 1
    classified_email_repository.find_by_account_and_imap_id.assert_called_once_with(1, "12345")


def test_get_all_emails_no_filters(classified_email_service, classified_email_repository):
    from domain.entities.email import ClassifiedEmail as ClassifiedEmailEntity

    mock_entities = [
        ClassifiedEmailEntity(id=1, email_account_id=1, imap_id="123", sender="s1@test.com",
                             recipients="r1@test.com", subject=None, email_date=None,
                             classification=None, emergency_level=None, abstract=None, lead_id=None,
                             created_at=datetime.now(), updated_at=datetime.now()),
        ClassifiedEmailEntity(id=2, email_account_id=1, imap_id="456", sender="s2@test.com",
                             recipients="r2@test.com", subject=None, email_date=None,
                             classification=None, emergency_level=None, abstract=None, lead_id=None,
                             created_at=datetime.now(), updated_at=datetime.now())
    ]
    classified_email_repository.find_all.return_value = mock_entities

    emails = classified_email_service.get_all_emails()

    assert len(emails) == 2
    classified_email_repository.find_all.assert_called_once()


def test_get_all_emails_with_filters(classified_email_service, classified_email_repository):
    from domain.entities.email import ClassifiedEmail as ClassifiedEmailEntity

    mock_entities = [
        ClassifiedEmailEntity(id=1, email_account_id=1, imap_id="123", sender="s@test.com",
                             recipients="r@test.com", subject=None, email_date=None,
                             emergency_level=5, classification="urgent",
                             abstract=None, lead_id=10, created_at=datetime.now(), updated_at=datetime.now())
    ]
    classified_email_repository.find_all.return_value = mock_entities

    emails = classified_email_service.get_all_emails(
        email_account_id=1,
        emergency_level=5,
        classification="urgent",
        lead_id=10
    )

    # Verify filters were passed to repository
    classified_email_repository.find_all.assert_called_once_with(
        email_account_id=1,
        emergency_level=5,
        classification="urgent",
        lead_id=10
    )
    assert len(emails) == 1


def test_update_classification_success(classified_email_service, classified_email_repository):
    from domain.entities.email import ClassifiedEmail as ClassifiedEmailEntity

    mock_entity = ClassifiedEmailEntity(
        id=1,
        email_account_id=1,
        imap_id="123",
        sender="s@test.com",
        recipients="r@test.com",
        subject=None,
        email_date=None,
        classification="old_classification",
        emergency_level=2,
        abstract="old abstract",
        lead_id=None,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    classified_email_repository.find_by_id.return_value = mock_entity

    # Mock update to modify and return entity
    def update_side_effect(entity):
        entity.classification = "new_classification"
        entity.emergency_level = 4
        entity.abstract = "new abstract"
        return entity
    classified_email_repository.update.side_effect = update_side_effect

    update_data = ClassifiedEmailUpdate(
        classification="new_classification",
        emergency_level=4,
        abstract="new abstract",
        change_reason="LLM re-evaluated"
    )

    email = classified_email_service.update_classification(1, update_data)

    # Verify history was saved
    classified_email_repository.save_history.assert_called_once()
    history_call = classified_email_repository.save_history.call_args[0][0]
    assert history_call.classification == "old_classification"
    assert history_call.change_reason == "LLM re-evaluated"

    # Verify email was updated
    assert email.classification == "new_classification"
    assert email.emergency_level == 4
    assert email.abstract == "new abstract"


def test_update_classification_not_found(classified_email_service, classified_email_repository):
    classified_email_repository.find_by_id.return_value = None

    update_data = ClassifiedEmailUpdate(classification="new")
    email = classified_email_service.update_classification(999, update_data)

    assert email is None


def test_update_classification_invalid_emergency_level(classified_email_service, classified_email_repository):
    from domain.entities.email import ClassifiedEmail as ClassifiedEmailEntity

    mock_entity = ClassifiedEmailEntity(
        id=1, email_account_id=1, imap_id="123", sender="s@test.com",
        recipients="r@test.com", subject=None, email_date=None,
        classification=None, emergency_level=None, abstract=None, lead_id=None,
        created_at=datetime.now(), updated_at=datetime.now()
    )
    classified_email_repository.find_by_id.return_value = mock_entity

    update_data = ClassifiedEmailUpdate(emergency_level=0)

    with pytest.raises(ValueError, match="Emergency level must be between 1 and 5"):
        classified_email_service.update_classification(1, update_data)


def test_delete_email_success(classified_email_service, classified_email_repository):
    from domain.entities.email import ClassifiedEmail as ClassifiedEmailEntity

    mock_entity = ClassifiedEmailEntity(
        id=1, email_account_id=1, imap_id="123", sender="s@test.com",
        recipients="r@test.com", subject=None, email_date=None,
        classification=None, emergency_level=None, abstract=None, lead_id=None,
        created_at=datetime.now(), updated_at=datetime.now()
    )
    classified_email_repository.find_by_id.return_value = mock_entity
    classified_email_repository.delete.return_value = True

    success = classified_email_service.delete_email(1)

    assert success is True
    classified_email_repository.delete.assert_called_once_with(1)


def test_delete_email_not_found(classified_email_service, classified_email_repository):
    classified_email_repository.find_by_id.return_value = None

    success = classified_email_service.delete_email(999)

    assert success is False
