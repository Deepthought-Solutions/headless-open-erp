"""Position domain entity - pure business object."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Position:
    """Pure domain entity representing a job position."""

    id: Optional[int]
    title: str
