"""Email repository interfaces - domain layer defines the contract."""

from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.email import EmailAccount, ClassifiedEmail, EmailClassificationHistory


class EmailAccountRepository(ABC):
    """Abstract repository for EmailAccount - infrastructure implements this."""

    @abstractmethod
    def save(self, account: EmailAccount) -> EmailAccount:
        """Persist a new email account."""
        pass

    @abstractmethod
    def find_by_id(self, account_id: int) -> Optional[EmailAccount]:
        """Find email account by ID."""
        pass

    @abstractmethod
    def find_all(self) -> List[EmailAccount]:
        """Get all email accounts."""
        pass

    @abstractmethod
    def update(self, account: EmailAccount) -> EmailAccount:
        """Update existing email account."""
        pass

    @abstractmethod
    def delete(self, account_id: int) -> bool:
        """Delete an email account."""
        pass


class ClassifiedEmailRepository(ABC):
    """Abstract repository for ClassifiedEmail - infrastructure implements this."""

    @abstractmethod
    def save(self, email: ClassifiedEmail) -> ClassifiedEmail:
        """Persist a new classified email."""
        pass

    @abstractmethod
    def find_by_id(self, email_id: int) -> Optional[ClassifiedEmail]:
        """Find classified email by ID."""
        pass

    @abstractmethod
    def find_by_account_and_imap_id(self, account_id: int, imap_id: str) -> Optional[ClassifiedEmail]:
        """Find email by account and IMAP ID."""
        pass

    @abstractmethod
    def find_all(
        self,
        email_account_id: Optional[int] = None,
        emergency_level: Optional[int] = None,
        classification: Optional[str] = None,
        lead_id: Optional[int] = None
    ) -> List[ClassifiedEmail]:
        """Find all classified emails with optional filters."""
        pass

    @abstractmethod
    def update(self, email: ClassifiedEmail) -> ClassifiedEmail:
        """Update existing classified email."""
        pass

    @abstractmethod
    def delete(self, email_id: int) -> bool:
        """Delete a classified email."""
        pass

    @abstractmethod
    def save_history(self, history: EmailClassificationHistory) -> EmailClassificationHistory:
        """Save classification history entry."""
        pass

    @abstractmethod
    def get_history(self, email_id: int) -> List[EmailClassificationHistory]:
        """Get classification history for an email."""
        pass
