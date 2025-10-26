"""Note repository interface - domain layer defines the contract."""

from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.note import Note, NoteReason


class NoteRepository(ABC):
    """Abstract repository for Note - infrastructure implements this."""

    @abstractmethod
    def save(self, note: Note) -> Note:
        """Persist a new note."""
        pass

    @abstractmethod
    def find_by_id(self, note_id: int) -> Optional[Note]:
        """Find note by ID."""
        pass

    @abstractmethod
    def find_by_lead_id(self, lead_id: int) -> List[Note]:
        """Find all notes for a lead."""
        pass

    @abstractmethod
    def find_reason_by_name(self, name: str) -> Optional[NoteReason]:
        """Find note reason by name."""
        pass

    @abstractmethod
    def get_all_reasons(self) -> List[NoteReason]:
        """Get all available note reasons."""
        pass
