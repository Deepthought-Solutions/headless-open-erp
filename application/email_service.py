import logging
import sys
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from domain.orm import EmailAccount, ClassifiedEmail, EmailClassificationHistory
from domain.contact import (
    EmailAccountCreate, EmailAccountUpdate,
    ClassifiedEmailCreate, ClassifiedEmailUpdate
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.handlers = []
logger.addHandler(handler)
logger.propagate = False


class EmailAccountService:
    def __init__(self, db: Session):
        self.db = db

    def create_account(self, account_data: EmailAccountCreate) -> EmailAccount:
        """Create a new email account configuration."""
        try:
            account = EmailAccount(
                name=account_data.name,
                imap_host=account_data.imap_host,
                imap_port=account_data.imap_port,
                imap_username=account_data.imap_username,
                imap_password=account_data.imap_password,
                imap_use_ssl=1 if account_data.imap_use_ssl else 0
            )
            self.db.add(account)
            self.db.commit()
            self.db.refresh(account)
            logger.info(f"Created email account: {account.name}")
            return account
        except Exception as e:
            logger.exception("Error creating email account")
            self.db.rollback()
            raise e

    def get_account_by_id(self, account_id: int) -> Optional[EmailAccount]:
        """Get email account by ID."""
        try:
            return self.db.query(EmailAccount).filter(EmailAccount.id == account_id).first()
        except Exception as e:
            logger.exception(f"Error getting email account {account_id}")
            raise e

    def get_all_accounts(self) -> List[EmailAccount]:
        """Get all email accounts."""
        try:
            return self.db.query(EmailAccount).all()
        except Exception as e:
            logger.exception("Error getting all email accounts")
            raise e

    def update_account(self, account_id: int, update_data: EmailAccountUpdate) -> Optional[EmailAccount]:
        """Update an email account."""
        try:
            account = self.get_account_by_id(account_id)
            if not account:
                return None

            update_dict = update_data.model_dump(exclude_unset=True)

            # Convert boolean to integer for SQLite compatibility
            if 'imap_use_ssl' in update_dict:
                update_dict['imap_use_ssl'] = 1 if update_dict['imap_use_ssl'] else 0

            for key, value in update_dict.items():
                setattr(account, key, value)

            self.db.commit()
            self.db.refresh(account)
            logger.info(f"Updated email account: {account.name}")
            return account
        except Exception as e:
            logger.exception(f"Error updating email account {account_id}")
            self.db.rollback()
            raise e

    def delete_account(self, account_id: int) -> bool:
        """Delete an email account."""
        try:
            account = self.get_account_by_id(account_id)
            if not account:
                return False

            self.db.delete(account)
            self.db.commit()
            logger.info(f"Deleted email account: {account.name}")
            return True
        except Exception as e:
            logger.exception(f"Error deleting email account {account_id}")
            self.db.rollback()
            raise e


class ClassifiedEmailService:
    def __init__(self, db: Session):
        self.db = db

    def create_classified_email(self, email_data: ClassifiedEmailCreate) -> ClassifiedEmail:
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
            existing = self.db.query(ClassifiedEmail).filter(
                ClassifiedEmail.email_account_id == email_data.email_account_id,
                ClassifiedEmail.imap_id == email_data.imap_id
            ).first()

            if existing:
                logger.warning(f"Email already exists for account {email_data.email_account_id}, IMAP ID {email_data.imap_id}")
                raise ValueError("Email with this IMAP ID already exists for this account")

            email = ClassifiedEmail(
                email_account_id=email_data.email_account_id,
                imap_id=email_data.imap_id,
                sender=email_data.sender,
                recipients=email_data.recipients,
                subject=email_data.subject,
                email_date=email_data.email_date,
                classification=email_data.classification,
                emergency_level=email_data.emergency_level,
                abstract=email_data.abstract,
                lead_id=email_data.lead_id
            )
            self.db.add(email)
            self.db.commit()
            self.db.refresh(email)
            logger.info(f"Created classified email: {email.id} from {email.sender}")
            return email
        except Exception as e:
            logger.exception("Error creating classified email")
            self.db.rollback()
            raise e

    def get_email_by_id(self, email_id: int) -> Optional[ClassifiedEmail]:
        """Get classified email by ID with history."""
        try:
            return self.db.query(ClassifiedEmail).options(
                joinedload(ClassifiedEmail.classification_history)
            ).filter(ClassifiedEmail.id == email_id).first()
        except Exception as e:
            logger.exception(f"Error getting classified email {email_id}")
            raise e

    def get_email_by_imap_id(self, email_account_id: int, imap_id: str) -> Optional[ClassifiedEmail]:
        """Get classified email by account and IMAP ID."""
        try:
            return self.db.query(ClassifiedEmail).filter(
                ClassifiedEmail.email_account_id == email_account_id,
                ClassifiedEmail.imap_id == imap_id
            ).first()
        except Exception as e:
            logger.exception(f"Error getting email by IMAP ID {imap_id}")
            raise e

    def get_all_emails(self,
                       email_account_id: Optional[int] = None,
                       emergency_level: Optional[int] = None,
                       classification: Optional[str] = None,
                       lead_id: Optional[int] = None) -> List[ClassifiedEmail]:
        """Get all classified emails with optional filters."""
        try:
            query = self.db.query(ClassifiedEmail)

            if email_account_id is not None:
                query = query.filter(ClassifiedEmail.email_account_id == email_account_id)
            if emergency_level is not None:
                query = query.filter(ClassifiedEmail.emergency_level == emergency_level)
            if classification is not None:
                query = query.filter(ClassifiedEmail.classification == classification)
            if lead_id is not None:
                query = query.filter(ClassifiedEmail.lead_id == lead_id)

            return query.order_by(ClassifiedEmail.email_date.desc()).all()
        except Exception as e:
            logger.exception("Error getting classified emails")
            raise e

    def update_classification(self, email_id: int, update_data: ClassifiedEmailUpdate) -> Optional[ClassifiedEmail]:
        """Update email classification and create history record."""
        try:
            email = self.get_email_by_id(email_id)
            if not email:
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
                history = EmailClassificationHistory(
                    classified_email_id=email.id,
                    classification=email.classification,
                    emergency_level=email.emergency_level,
                    abstract=email.abstract,
                    change_reason=update_data.change_reason
                )
                self.db.add(history)

            # Update email
            update_dict = update_data.model_dump(exclude_unset=True, exclude={'change_reason'})
            for key, value in update_dict.items():
                setattr(email, key, value)

            self.db.commit()
            self.db.refresh(email)
            logger.info(f"Updated classification for email {email.id}")
            return email
        except Exception as e:
            logger.exception(f"Error updating classified email {email_id}")
            self.db.rollback()
            raise e

    def delete_email(self, email_id: int) -> bool:
        """Delete a classified email and its history."""
        try:
            email = self.get_email_by_id(email_id)
            if not email:
                return False

            self.db.delete(email)
            self.db.commit()
            logger.info(f"Deleted classified email {email_id}")
            return True
        except Exception as e:
            logger.exception(f"Error deleting classified email {email_id}")
            self.db.rollback()
            raise e
