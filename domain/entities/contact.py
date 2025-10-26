"""Contact domain entity - pure business object."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Contact:
    """Pure domain entity representing a contact person."""

    id: Optional[int]
    name: str
    email: str
    phone: Optional[str]
    job_title: Optional[str]
    conscent: bool
    created_at: datetime
    updated_at: datetime

    def is_executive(self) -> bool:
        """Check if contact has an executive role."""
        if not self.job_title:
            return False
        executive_roles = {'ceo', 'cto', 'cfo', 'manager', 'director'}
        return any(role in self.job_title.lower() for role in executive_roles)
