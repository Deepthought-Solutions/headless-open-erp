"""Lead scoring domain service - pure business logic."""

from typing import List
from domain.contact import LeadPayload


class LeadScoringService:
    """Domain service for lead scoring business logic - no dependencies."""

    def calculate_maturity_score(self, payload: LeadPayload) -> int:
        """
        Calculate maturity score based on company size, estimated users,
        concerns count, and job title.

        Returns: Score from 0-5
        """
        score = 0
        if payload.company_size and payload.company_size > 100:
            score += 1
        if payload.estimated_users and payload.estimated_users > 50:
            score += 1
        if len(payload.concerns) > 2:
            score += 1
        if payload.job_title and any(
            role in payload.job_title.lower()
            for role in ['manager', 'director', 'cto', 'ceo']
        ):
            score += 1

        return min(score, 5)

    def recommend_pack(self, concerns: List[str]) -> str:
        """
        Recommend a pack based on concerns.

        Returns: Pack name ('confiance', 'croissance', or 'conformité')
        """
        pack_name = "conformité"  # Default

        if any("confiance" in c.lower() for c in concerns):
            pack_name = "confiance"
        elif any("croissance" in c.lower() for c in concerns):
            pack_name = "croissance"

        return pack_name
