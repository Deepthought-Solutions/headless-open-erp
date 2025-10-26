"""Lead repository interface - domain layer defines the contract."""

from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.lead import Lead


class LeadRepository(ABC):
    """Abstract repository for Lead aggregate - infrastructure implements this."""

    @abstractmethod
    def save(self, lead: Lead) -> Lead:
        """Persist a new lead."""
        pass

    @abstractmethod
    def find_by_id(self, lead_id: int) -> Optional[Lead]:
        """Find lead by ID with all relationships loaded."""
        pass

    @abstractmethod
    def find_all(self) -> List[Lead]:
        """Get all leads with relationships."""
        pass

    @abstractmethod
    def update(self, lead: Lead) -> Lead:
        """Update existing lead."""
        pass

    @abstractmethod
    def delete(self, lead_id: int) -> bool:
        """Delete a lead."""
        pass
