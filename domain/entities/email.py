"""Email domain entities - pure business objects."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class EmailAccount:
    """Pure domain entity representing an IMAP email account."""

    id: Optional[int]
    name: str
    imap_host: str
    imap_port: int
    imap_username: str
    imap_password: str
    imap_use_ssl: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class ClassifiedEmail:
    """Pure domain entity representing a classified email."""

    id: Optional[int]
    email_account_id: int
    imap_id: str
    sender: str
    recipients: str
    subject: Optional[str]
    email_date: Optional[datetime]
    classification: Optional[str]
    emergency_level: Optional[int]
    abstract: Optional[str]
    lead_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    def is_emergency(self) -> bool:
        """Check if email is marked as emergency (level 4-5)."""
        return self.emergency_level is not None and self.emergency_level >= 4

    def has_classification(self) -> bool:
        """Check if email has been classified."""
        return self.classification is not None


@dataclass
class EmailClassificationHistory:
    """Pure domain entity representing email re-classification history."""

    id: Optional[int]
    classified_email_id: int
    classification: Optional[str]
    emergency_level: Optional[int]
    abstract: Optional[str]
    changed_at: datetime
    change_reason: Optional[str]
