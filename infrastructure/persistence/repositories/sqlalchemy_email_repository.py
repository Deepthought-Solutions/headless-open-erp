"""SQLAlchemy implementation of Email repositories."""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from domain.repositories.email_repository import EmailAccountRepository, ClassifiedEmailRepository
from domain.entities.email import EmailAccount, ClassifiedEmail, EmailClassificationHistory
from infrastructure.persistence.models import (
    EmailAccountModel as EmailAccountORM,
    ClassifiedEmailModel as ClassifiedEmailORM,
    EmailClassificationHistoryModel as EmailClassificationHistoryORM
)
from infrastructure.persistence.mappers.email_mapper import (
    EmailAccountMapper,
    ClassifiedEmailMapper,
    EmailClassificationHistoryMapper
)


class SqlAlchemyEmailAccountRepository(EmailAccountRepository):
    """Concrete repository implementation using SQLAlchemy."""

    def __init__(self, session: Session):
        self._session = session

    def save(self, account: EmailAccount) -> EmailAccount:
        """Persist a new email account."""
        model = EmailAccountMapper.to_model(account)
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return EmailAccountMapper.to_domain(model)

    def find_by_id(self, account_id: int) -> Optional[EmailAccount]:
        """Find email account by ID."""
        model = self._session.query(EmailAccountORM).filter(
            EmailAccountORM.id == account_id
        ).one_or_none()

        return EmailAccountMapper.to_domain(model) if model else None

    def find_all(self) -> List[EmailAccount]:
        """Get all email accounts."""
        models = self._session.query(EmailAccountORM).all()
        return [EmailAccountMapper.to_domain(m) for m in models]

    def update(self, account: EmailAccount) -> EmailAccount:
        """Update existing email account."""
        model = self._session.query(EmailAccountORM).filter(
            EmailAccountORM.id == account.id
        ).one_or_none()

        if not model:
            raise ValueError(f"EmailAccount {account.id} not found")

        # Update fields
        model.name = account.name
        model.imap_host = account.imap_host
        model.imap_port = account.imap_port
        model.imap_username = account.imap_username
        model.imap_password = account.imap_password
        model.imap_use_ssl = 1 if account.imap_use_ssl else 0
        model.updated_at = account.updated_at

        self._session.commit()
        self._session.refresh(model)
        return EmailAccountMapper.to_domain(model)

    def delete(self, account_id: int) -> bool:
        """Delete an email account."""
        model = self._session.query(EmailAccountORM).filter(
            EmailAccountORM.id == account_id
        ).one_or_none()

        if not model:
            return False

        self._session.delete(model)
        self._session.commit()
        return True


class SqlAlchemyClassifiedEmailRepository(ClassifiedEmailRepository):
    """Concrete repository implementation using SQLAlchemy."""

    def __init__(self, session: Session):
        self._session = session

    def save(self, email: ClassifiedEmail) -> ClassifiedEmail:
        """Persist a new classified email."""
        model = ClassifiedEmailMapper.to_model(email)
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return ClassifiedEmailMapper.to_domain(model)

    def find_by_id(self, email_id: int) -> Optional[ClassifiedEmail]:
        """Find classified email by ID."""
        model = self._session.query(ClassifiedEmailORM).options(
            joinedload(ClassifiedEmailORM.classification_history)
        ).filter(
            ClassifiedEmailORM.id == email_id
        ).one_or_none()

        return ClassifiedEmailMapper.to_domain(model) if model else None

    def find_by_account_and_imap_id(
        self, account_id: int, imap_id: str
    ) -> Optional[ClassifiedEmail]:
        """Find email by account and IMAP ID."""
        model = self._session.query(ClassifiedEmailORM).filter(
            ClassifiedEmailORM.email_account_id == account_id,
            ClassifiedEmailORM.imap_id == imap_id
        ).one_or_none()

        return ClassifiedEmailMapper.to_domain(model) if model else None

    def find_all(
        self,
        email_account_id: Optional[int] = None,
        emergency_level: Optional[int] = None,
        classification: Optional[str] = None,
        lead_id: Optional[int] = None
    ) -> List[ClassifiedEmail]:
        """Find all classified emails with optional filters."""
        query = self._session.query(ClassifiedEmailORM)

        if email_account_id is not None:
            query = query.filter(ClassifiedEmailORM.email_account_id == email_account_id)
        if emergency_level is not None:
            query = query.filter(ClassifiedEmailORM.emergency_level == emergency_level)
        if classification is not None:
            query = query.filter(ClassifiedEmailORM.classification.ilike(f"%{classification}%"))
        if lead_id is not None:
            query = query.filter(ClassifiedEmailORM.lead_id == lead_id)

        models = query.all()
        return [ClassifiedEmailMapper.to_domain(m) for m in models]

    def update(self, email: ClassifiedEmail) -> ClassifiedEmail:
        """Update existing classified email."""
        model = self._session.query(ClassifiedEmailORM).filter(
            ClassifiedEmailORM.id == email.id
        ).one_or_none()

        if not model:
            raise ValueError(f"ClassifiedEmail {email.id} not found")

        # Update fields
        model.classification = email.classification
        model.emergency_level = email.emergency_level
        model.abstract = email.abstract
        model.lead_id = email.lead_id
        model.updated_at = email.updated_at

        self._session.commit()
        self._session.refresh(model)
        return ClassifiedEmailMapper.to_domain(model)

    def delete(self, email_id: int) -> bool:
        """Delete a classified email."""
        model = self._session.query(ClassifiedEmailORM).filter(
            ClassifiedEmailORM.id == email_id
        ).one_or_none()

        if not model:
            return False

        self._session.delete(model)
        self._session.commit()
        return True

    def save_history(
        self, history: EmailClassificationHistory
    ) -> EmailClassificationHistory:
        """Save classification history entry."""
        model = EmailClassificationHistoryMapper.to_model(history)
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return EmailClassificationHistoryMapper.to_domain(model)

    def get_history(self, email_id: int) -> List[EmailClassificationHistory]:
        """Get classification history for an email."""
        models = self._session.query(EmailClassificationHistoryORM).filter(
            EmailClassificationHistoryORM.classified_email_id == email_id
        ).order_by(EmailClassificationHistoryORM.changed_at.desc()).all()

        return [EmailClassificationHistoryMapper.to_domain(m) for m in models]
