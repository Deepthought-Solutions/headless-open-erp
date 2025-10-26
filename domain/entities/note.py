"""Note domain entity - pure business object."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class NoteReason:
    """Value object for note reason."""

    id: Optional[int]
    name: str


@dataclass
class Note:
    """Pure domain entity representing a note on a lead."""

    id: Optional[int]
    note: str
    created_at: datetime
    author_name: str
    lead_id: int
    reason: NoteReason
