import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from domain.repositories.email_repository import EmailAccountRepository, ClassifiedEmailRepository
from domain.entities.email import EmailAccount, ClassifiedEmail, EmailClassificationHistory
from domain.contact import (
    EmailAccountCreate, EmailAccountUpdate,
    ClassifiedEmailCreate, ClassifiedEmailUpdate
)
# Still need ORM for API compatibility
from infrastructure.persistence.models import EmailAccountModel as EmailAccountORM, ClassifiedEmailModel as ClassifiedEmailORM

logger = logging.getLogger(__name__)


class EmailAccountService:
    """Application service for email account operations - uses repository pattern."""

    def __init__(self, email_account_repository: EmailAccountRepository):
        self._email_account_repo = email_account_repository

    def create_account(self, account_data: EmailAccountCreate) -> EmailAccountORM:
        """Create a new email account configuration."""
        try:
            account_entity = EmailAccount(
                id=None,
                name=account_data.name,
                imap_host=account_data.imap_host,
                imap_port=account_data.imap_port,
                imap_username=account_data.imap_username,
                imap_password=account_data.imap_password,
                imap_use_ssl=account_data.imap_use_ssl,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            saved_entity = self._email_account_repo.save(account_entity)
            logger.info(f"Created email account: {saved_entity.name}")

            # Return ORM for API compatibility
            from infrastructure.persistence.mappers.email_mapper import EmailAccountMapper
            return EmailAccountMapper.to_model(saved_entity)
        except Exception as e:
            logger.exception("Error creating email account")
            raise e

    def get_account_by_id(self, account_id: int) -> Optional[EmailAccountORM]:
        """Get email account by ID."""
        try:
            entity = self._email_account_repo.find_by_id(account_id)
            if not entity:
                return None

            # Return ORM for API compatibility
            from infrastructure.persistence.mappers.email_mapper import EmailAccountMapper
            return EmailAccountMapper.to_model(entity)
        except Exception as e:
            logger.exception(f"Error getting email account {account_id}")
            raise e

    def get_all_accounts(self) -> List[EmailAccountORM]:
        """Get all email accounts."""
        try:
            entities = self._email_account_repo.find_all()

            # Return ORMs for API compatibility
            from infrastructure.persistence.mappers.email_mapper import EmailAccountMapper
            return [EmailAccountMapper.to_model(e) for e in entities]
        except Exception as e:
            logger.exception("Error getting all email accounts")
            raise e

    def update_account(self, account_id: int, update_data: EmailAccountUpdate) -> Optional[EmailAccountORM]:
        """Update an email account."""
        try:
            entity = self._email_account_repo.find_by_id(account_id)
            if not entity:
                return None

            update_dict = update_data.model_dump(exclude_unset=True)

            # Update entity fields
            for key, value in update_dict.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)

            entity.updated_at = datetime.now()
            updated_entity = self._email_account_repo.update(entity)
            logger.info(f"Updated email account: {updated_entity.name}")

            # Return ORM for API compatibility
            from infrastructure.persistence.mappers.email_mapper import EmailAccountMapper
            return EmailAccountMapper.to_model(updated_entity)
        except Exception as e:
            logger.exception(f"Error updating email account {account_id}")
            raise e

    def delete_account(self, account_id: int) -> bool:
        """Delete an email account."""
        try:
            entity = self._email_account_repo.find_by_id(account_id)
            if not entity:
                return False

            result = self._email_account_repo.delete(account_id)
            if result:
                logger.info(f"Deleted email account: {entity.name}")
            return result
        except Exception as e:
            logger.exception(f"Error deleting email account {account_id}")
            raise e


class ClassifiedEmailService:
    """Application service for classified email operations - uses repository pattern."""

    def __init__(self, session: Session, classified_email_repository: ClassifiedEmailRepository):
        self._session = session
        self._classified_email_repo = classified_email_repository

    def create_classified_email(self, email_data: ClassifiedEmailCreate) -> ClassifiedEmailORM:
        """Create a new classified email entry."""
        try:
            # Validate emergency level
            if email_data.emergency_level is not None:
                if not (1 <= email_data.emergency_level <= 5):
                    raise ValueError("Emergency level must be between 1 and 5")

            # Validate abstract length
            if email_data.abstract and len(email_data.abstract) > 200:
                raise ValueError("Abstract must be 200 characters or less")

            # Check if email already exists (same account + imap_id)
            existing = self._classified_email_repo.find_by_account_and_imap_id(
                email_data.email_account_id,
                email_data.imap_id
            )

            if existing:
                logger.warning(f"Email already exists for account {email_data.email_account_id}, IMAP ID {email_data.imap_id}")
                raise ValueError("Email with this IMAP ID already exists for this account")

            email_entity = ClassifiedEmail(
                id=None,
                email_account_id=email_data.email_account_id,
                imap_id=email_data.imap_id,
                sender=email_data.sender,
                recipients=email_data.recipients,
                subject=email_data.subject,
                email_date=email_data.email_date,
                classification=email_data.classification,
                emergency_level=email_data.emergency_level,
                abstract=email_data.abstract,
                lead_id=email_data.lead_id,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            saved_entity = self._classified_email_repo.save(email_entity)
            logger.info(f"Created classified email: {saved_entity.id} from {saved_entity.sender}")

            # Return ORM for API compatibility
            from infrastructure.persistence.mappers.email_mapper import ClassifiedEmailMapper
            return ClassifiedEmailMapper.to_model(saved_entity)
        except Exception as e:
            logger.exception("Error creating classified email")
            raise e

    def get_email_by_id(self, email_id: int) -> Optional[ClassifiedEmailORM]:
        """Get classified email by ID with history."""
        try:
            # Query ORM directly to preserve relationships
            model = self._session.query(ClassifiedEmailORM).options(
                joinedload(ClassifiedEmailORM.classification_history)
            ).filter(ClassifiedEmailORM.id == email_id).one_or_none()
            return model
        except Exception as e:
            logger.exception(f"Error getting classified email {email_id}")
            raise e

    def get_email_by_imap_id(self, email_account_id: int, imap_id: str) -> Optional[ClassifiedEmailORM]:
        """Get classified email by account and IMAP ID."""
        try:
            entity = self._classified_email_repo.find_by_account_and_imap_id(email_account_id, imap_id)
            if not entity:
                return None

            # Return ORM for API compatibility
            from infrastructure.persistence.mappers.email_mapper import ClassifiedEmailMapper
            return ClassifiedEmailMapper.to_model(entity)
        except Exception as e:
            logger.exception(f"Error getting email by IMAP ID {imap_id}")
            raise e

    def get_all_emails(self,
                       email_account_id: Optional[int] = None,
                       emergency_level: Optional[int] = None,
                       classification: Optional[str] = None,
                       lead_id: Optional[int] = None) -> List[ClassifiedEmailORM]:
        """Get all classified emails with optional filters."""
        try:
            entities = self._classified_email_repo.find_all(
                email_account_id=email_account_id,
                emergency_level=emergency_level,
                classification=classification,
                lead_id=lead_id
            )

            # Return ORMs for API compatibility
            from infrastructure.persistence.mappers.email_mapper import ClassifiedEmailMapper
            return [ClassifiedEmailMapper.to_model(e) for e in entities]
        except Exception as e:
            logger.exception("Error getting classified emails")
            raise e

    def update_classification(self, email_id: int, update_data: ClassifiedEmailUpdate) -> Optional[ClassifiedEmailORM]:
        """Update email classification and create history record."""
        try:
            entity = self._classified_email_repo.find_by_id(email_id)
            if not entity:
                return None

            # Validate emergency level if provided
            if update_data.emergency_level is not None:
                if not (1 <= update_data.emergency_level <= 5):
                    raise ValueError("Emergency level must be between 1 and 5")

            # Validate abstract length if provided
            if update_data.abstract and len(update_data.abstract) > 200:
                raise ValueError("Abstract must be 200 characters or less")

            # Create history record before updating
            if any([
                update_data.classification is not None,
                update_data.emergency_level is not None,
                update_data.abstract is not None
            ]):
                history_entity = EmailClassificationHistory(
                    id=None,
                    classified_email_id=entity.id,
                    classification=entity.classification,
                    emergency_level=entity.emergency_level,
                    abstract=entity.abstract,
                    changed_at=datetime.now(),
                    change_reason=update_data.change_reason
                )
                self._classified_email_repo.save_history(history_entity)

            # Update email
            update_dict = update_data.model_dump(exclude_unset=True, exclude={'change_reason'})
            for key, value in update_dict.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)

            entity.updated_at = datetime.now()
            updated_entity = self._classified_email_repo.update(entity)
            logger.info(f"Updated classification for email {updated_entity.id}")

            # Return ORM for API compatibility
            from infrastructure.persistence.mappers.email_mapper import ClassifiedEmailMapper
            return ClassifiedEmailMapper.to_model(updated_entity)
        except Exception as e:
            logger.exception(f"Error updating classified email {email_id}")
            raise e

    def delete_email(self, email_id: int) -> bool:
        """Delete a classified email and its history."""
        try:
            entity = self._classified_email_repo.find_by_id(email_id)
            if not entity:
                return False

            result = self._classified_email_repo.delete(email_id)
            if result:
                logger.info(f"Deleted classified email {email_id}")
            return result
        except Exception as e:
            logger.exception(f"Error deleting classified email {email_id}")
            raise e
