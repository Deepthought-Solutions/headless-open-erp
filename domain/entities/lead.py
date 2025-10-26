"""Lead domain entity - pure business object with business logic."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class LeadStatus:
    """Value object for lead status."""

    id: Optional[int]
    name: str


@dataclass
class LeadUrgency:
    """Value object for lead urgency."""

    id: Optional[int]
    name: str


@dataclass
class RecommendedPack:
    """Value object for recommended pack."""

    id: Optional[int]
    name: str


@dataclass
class Lead:
    """Pure domain entity representing a sales lead with business logic."""

    id: Optional[int]
    submission_date: datetime
    estimated_users: Optional[int]
    problem_summary: Optional[str]
    maturity_score: Optional[int]
    altcha_solution: Optional[str]
    fingerprint_visitor_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    # Related entities (not IDs - composition over FK references)
    contact: 'Contact'
    company: 'Company'
    status: LeadStatus
    urgency: LeadUrgency
    recommended_pack: Optional[RecommendedPack]
    positions: List['Position']
    concerns: List['Concern']

    def calculate_potential_score(self) -> int:
        """
        Business logic: Calculate lead potential score based on company size,
        urgency, and contact seniority.

        Returns:
            Score from 0-8 indicating lead quality
        """
        score = 0

        # Company size scoring
        if self.company and self.company.size:
            if self.company.size > 1000:
                score += 3
            elif self.company.size > 250:
                score += 2
            else:
                score += 1

        # Urgency scoring
        if self.urgency:
            if self.urgency.name == "immédiat":
                score += 3
            elif self.urgency.name == "ce mois":
                score += 2

        # Contact seniority scoring
        if self.contact and self.contact.is_executive():
            score += 2

        return score

    def is_high_priority(self) -> bool:
        """Check if this is a high-priority lead."""
        return self.calculate_potential_score() >= 6

    def has_urgent_timeline(self) -> bool:
        """Check if lead has urgent timeline."""
        return self.urgency and self.urgency.name == "immédiat"


# Import here to avoid circular dependency
from .contact import Contact
from .company import Company
from .position import Position
from .concern import Concern
