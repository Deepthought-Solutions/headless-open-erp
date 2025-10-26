"""Fingerprint repository interface - domain layer defines the contract."""

from abc import ABC, abstractmethod
from typing import Optional
from domain.entities.fingerprint import Fingerprint


class FingerprintRepository(ABC):
    """Abstract repository for Fingerprint - infrastructure implements this."""

    @abstractmethod
    def save(self, fingerprint: Fingerprint) -> Fingerprint:
        """Persist a new fingerprint."""
        pass

    @abstractmethod
    def find_by_visitor_id(self, visitor_id: str) -> Optional[Fingerprint]:
        """Find fingerprint by visitor ID."""
        pass

    @abstractmethod
    def exists(self, visitor_id: str) -> bool:
        """Check if fingerprint exists."""
        pass
