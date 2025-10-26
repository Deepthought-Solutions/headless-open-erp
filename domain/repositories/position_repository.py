"""Position repository interface - domain layer defines the contract."""

from abc import ABC, abstractmethod
from typing import Optional
from domain.entities.position import Position


class PositionRepository(ABC):
    """Abstract repository for Position - infrastructure implements this."""

    @abstractmethod
    def save(self, position: Position) -> Position:
        """Persist a new position."""
        pass

    @abstractmethod
    def find_by_title(self, title: str) -> Optional[Position]:
        """Find position by title."""
        pass

    @abstractmethod
    def find_by_id(self, position_id: int) -> Optional[Position]:
        """Find position by ID."""
        pass
