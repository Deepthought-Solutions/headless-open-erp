"""SQLAlchemy implementation of ContactRepository."""

from typing import Optional
from sqlalchemy.orm import Session

from domain.repositories.contact_repository import ContactRepository
from domain.entities.contact import Contact
from infrastructure.persistence.models import ContactModel as ContactORM
from infrastructure.persistence.mappers.contact_mapper import ContactMapper


class SqlAlchemyContactRepository(ContactRepository):
    """Concrete repository implementation using SQLAlchemy."""

    def __init__(self, session: Session):
        self._session = session

    def save(self, contact: Contact) -> Contact:
        """Persist a new or updated contact."""
        existing_model = self._session.query(ContactORM).filter(
            ContactORM.id == contact.id
        ).one_or_none() if contact.id else None

        if existing_model:
            # Update existing
            existing_model.name = contact.name
            existing_model.email = contact.email
            existing_model.phone = contact.phone
            existing_model.job_title = contact.job_title
            existing_model.conscent = contact.conscent
            existing_model.updated_at = contact.updated_at
            model = existing_model
        else:
            model = ContactMapper.to_model(contact)
            self._session.add(model)

        self._session.commit()
        self._session.refresh(model)
        return ContactMapper.to_domain(model)

    def find_by_email(self, email: str) -> Optional[Contact]:
        """Find contact by email address."""
        model = self._session.query(ContactORM).filter(
            ContactORM.email == email
        ).one_or_none()

        return ContactMapper.to_domain(model) if model else None

    def find_by_id(self, contact_id: int) -> Optional[Contact]:
        """Find contact by ID."""
        model = self._session.query(ContactORM).filter(
            ContactORM.id == contact_id
        ).one_or_none()

        return ContactMapper.to_domain(model) if model else None

    def update(self, contact: Contact) -> Contact:
        """Update existing contact."""
        return self.save(contact)
