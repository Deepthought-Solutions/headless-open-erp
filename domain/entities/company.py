"""Company domain entity - pure business object."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Company:
    """Pure domain entity representing a company."""

    id: Optional[int]
    name: str
    size: Optional[int]

    def is_enterprise(self) -> bool:
        """Check if company is enterprise-sized (>1000 employees)."""
        return self.size is not None and self.size > 1000

    def is_mid_market(self) -> bool:
        """Check if company is mid-market sized (250-1000 employees)."""
        return self.size is not None and 250 < self.size <= 1000

    def is_smb(self) -> bool:
        """Check if company is small/medium business (<250 employees)."""
        return self.size is not None and self.size <= 250
