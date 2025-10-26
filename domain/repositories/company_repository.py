"""Company repository interface - domain layer defines the contract."""

from abc import ABC, abstractmethod
from typing import Optional
from domain.entities.company import Company


class CompanyRepository(ABC):
    """Abstract repository for Company - infrastructure implements this."""

    @abstractmethod
    def save(self, company: Company) -> Company:
        """Persist a new company."""
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> Optional[Company]:
        """Find company by name."""
        pass

    @abstractmethod
    def find_by_id(self, company_id: int) -> Optional[Company]:
        """Find company by ID."""
        pass

    @abstractmethod
    def update(self, company: Company) -> Company:
        """Update existing company."""
        pass
