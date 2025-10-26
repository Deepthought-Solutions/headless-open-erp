"""Report repository interface - domain layer defines the contract."""

from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.report import Report


class ReportRepository(ABC):
    """Abstract repository for Report - infrastructure implements this."""

    @abstractmethod
    def save(self, report: Report) -> Report:
        """Persist a new report."""
        pass

    @abstractmethod
    def find_by_id(self, report_id: int) -> Optional[Report]:
        """Find report by ID."""
        pass

    @abstractmethod
    def find_by_visitor_id(self, visitor_id: str) -> List[Report]:
        """Find all reports for a visitor."""
        pass
