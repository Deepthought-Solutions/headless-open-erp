"""Concern repository interface - domain layer defines the contract."""

from abc import ABC, abstractmethod
from typing import Optional
from domain.entities.concern import Concern


class ConcernRepository(ABC):
    """Abstract repository for Concern - infrastructure implements this."""

    @abstractmethod
    def save(self, concern: Concern) -> Concern:
        """Persist a new concern."""
        pass

    @abstractmethod
    def find_by_label(self, label: str) -> Optional[Concern]:
        """Find concern by label."""
        pass

    @abstractmethod
    def find_by_id(self, concern_id: int) -> Optional[Concern]:
        """Find concern by ID."""
        pass
