"""Contact repository interface - domain layer defines the contract."""

from abc import ABC, abstractmethod
from typing import Optional
from domain.entities.contact import Contact


class ContactRepository(ABC):
    """Abstract repository for Contact - infrastructure implements this."""

    @abstractmethod
    def save(self, contact: Contact) -> Contact:
        """Persist a new contact."""
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Contact]:
        """Find contact by email address."""
        pass

    @abstractmethod
    def find_by_id(self, contact_id: int) -> Optional[Contact]:
        """Find contact by ID."""
        pass

    @abstractmethod
    def update(self, contact: Contact) -> Contact:
        """Update existing contact."""
        pass
