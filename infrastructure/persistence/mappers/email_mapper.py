"""Email mappers - convert between domain entities and ORM models."""

from domain.entities.email import EmailAccount, ClassifiedEmail, EmailClassificationHistory
from infrastructure.persistence.models import (
    EmailAccountModel as EmailAccountORM,
    ClassifiedEmailModel as ClassifiedEmailORM,
    EmailClassificationHistoryModel as EmailClassificationHistoryORM
)


class EmailAccountMapper:
    """Maps between EmailAccount domain entity and EmailAccount ORM."""

    @staticmethod
    def to_domain(model: EmailAccountORM) -> EmailAccount:
        """Convert ORM model to domain entity."""
        if not model:
            return None

        return EmailAccount(
            id=model.id,
            name=model.name,
            imap_host=model.imap_host,
            imap_port=model.imap_port,
            imap_username=model.imap_username,
            imap_password=model.imap_password,
            imap_use_ssl=bool(model.imap_use_ssl),
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    @staticmethod
    def to_model(entity: EmailAccount) -> EmailAccountORM:
        """Convert domain entity to ORM model."""
        if not entity:
            return None

        return EmailAccountORM(
            id=entity.id,
            name=entity.name,
            imap_host=entity.imap_host,
            imap_port=entity.imap_port,
            imap_username=entity.imap_username,
            imap_password=entity.imap_password,
            imap_use_ssl=1 if entity.imap_use_ssl else 0,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )


class ClassifiedEmailMapper:
    """Maps between ClassifiedEmail domain entity and ClassifiedEmail ORM."""

    @staticmethod
    def to_domain(model: ClassifiedEmailORM) -> ClassifiedEmail:
        """Convert ORM model to domain entity."""
        if not model:
            return None

        return ClassifiedEmail(
            id=model.id,
            email_account_id=model.email_account_id,
            imap_id=model.imap_id,
            sender=model.sender,
            recipients=model.recipients,
            subject=model.subject,
            email_date=model.email_date,
            classification=model.classification,
            emergency_level=model.emergency_level,
            abstract=model.abstract,
            lead_id=model.lead_id,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    @staticmethod
    def to_model(entity: ClassifiedEmail) -> ClassifiedEmailORM:
        """Convert domain entity to ORM model."""
        if not entity:
            return None

        return ClassifiedEmailORM(
            id=entity.id,
            email_account_id=entity.email_account_id,
            imap_id=entity.imap_id,
            sender=entity.sender,
            recipients=entity.recipients,
            subject=entity.subject,
            email_date=entity.email_date,
            classification=entity.classification,
            emergency_level=entity.emergency_level,
            abstract=entity.abstract,
            lead_id=entity.lead_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )


class EmailClassificationHistoryMapper:
    """Maps between EmailClassificationHistory domain entity and ORM model."""

    @staticmethod
    def to_domain(model: EmailClassificationHistoryORM) -> EmailClassificationHistory:
        """Convert ORM model to domain entity."""
        if not model:
            return None

        return EmailClassificationHistory(
            id=model.id,
            classified_email_id=model.classified_email_id,
            classification=model.classification,
            emergency_level=model.emergency_level,
            abstract=model.abstract,
            changed_at=model.changed_at,
            change_reason=model.change_reason
        )

    @staticmethod
    def to_model(entity: EmailClassificationHistory) -> EmailClassificationHistoryORM:
        """Convert domain entity to ORM model."""
        if not entity:
            return None

        return EmailClassificationHistoryORM(
            id=entity.id,
            classified_email_id=entity.classified_email_id,
            classification=entity.classification,
            emergency_level=entity.emergency_level,
            abstract=entity.abstract,
            changed_at=entity.changed_at,
            change_reason=entity.change_reason
        )
