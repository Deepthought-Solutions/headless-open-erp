"""Fingerprint domain entity - pure business object."""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any


@dataclass
class Fingerprint:
    """Pure domain entity representing a browser fingerprint."""

    visitor_id: str
    components: Dict[str, Any]
    created_at: datetime
