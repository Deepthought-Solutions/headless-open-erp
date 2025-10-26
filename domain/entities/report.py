"""Report domain entity - pure business object."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Report:
    """Pure domain entity representing a page visit report."""

    id: Optional[int]
    visitor_id: str
    page: str
    created_at: datetime
