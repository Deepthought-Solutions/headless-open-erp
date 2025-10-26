"""Concern domain entity - pure business object."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Concern:
    """Pure domain entity representing a business concern."""

    id: Optional[int]
    label: str
