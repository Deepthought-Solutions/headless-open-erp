"""Contact mapper - converts between domain entity and ORM model."""

from domain.entities.contact import Contact
from infrastructure.persistence.models import ContactModel as ContactORM


class ContactMapper:
    """Maps between Contact domain entity and Contact ORM."""

    @staticmethod
    def to_domain(model: ContactORM) -> Contact:
        """Convert ORM model to domain entity."""
        if not model:
            return None

        return Contact(
            id=model.id,
            name=model.name,
            email=model.email,
            phone=model.phone,
            job_title=model.job_title,
            conscent=model.conscent,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    @staticmethod
    def to_model(entity: Contact) -> ContactORM:
        """Convert domain entity to ORM model."""
        if not entity:
            return None

        return ContactORM(
            id=entity.id,
            name=entity.name,
            email=entity.email,
            phone=entity.phone,
            job_title=entity.job_title,
            conscent=entity.conscent,
            created_at=entity.created_at,
            updated_at=entity.updated_at
        )
