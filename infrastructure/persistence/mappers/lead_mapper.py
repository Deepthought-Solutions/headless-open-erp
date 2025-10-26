"""Lead mapper - converts between domain entity and ORM model."""

from typing import List
from domain.entities.lead import Lead, LeadStatus, LeadUrgency, RecommendedPack
from infrastructure.persistence.models import (
    LeadModel as LeadORM,
    LeadStatusModel as LeadStatusORM,
    LeadUrgencyModel as LeadUrgencyORM,
    RecommendedPackModel as RecommendedPackORM
)
from .contact_mapper import ContactMapper
from .company_mapper import CompanyMapper
from .position_mapper import PositionMapper
from .concern_mapper import ConcernMapper


class LeadStatusMapper:
    """Maps between LeadStatus domain value object and LeadStatus ORM."""

    @staticmethod
    def to_domain(model: LeadStatusORM) -> LeadStatus:
        """Convert ORM model to domain value object."""
        if not model:
            return None

        return LeadStatus(
            id=model.id,
            name=model.name
        )

    @staticmethod
    def to_model(entity: LeadStatus) -> LeadStatusORM:
        """Convert domain value object to ORM model."""
        if not entity:
            return None

        return LeadStatusORM(
            id=entity.id,
            name=entity.name
        )


class LeadUrgencyMapper:
    """Maps between LeadUrgency domain value object and LeadUrgency ORM."""

    @staticmethod
    def to_domain(model: LeadUrgencyORM) -> LeadUrgency:
        """Convert ORM model to domain value object."""
        if not model:
            return None

        return LeadUrgency(
            id=model.id,
            name=model.name
        )

    @staticmethod
    def to_model(entity: LeadUrgency) -> LeadUrgencyORM:
        """Convert domain value object to ORM model."""
        if not entity:
            return None

        return LeadUrgencyORM(
            id=entity.id,
            name=entity.name
        )


class RecommendedPackMapper:
    """Maps between RecommendedPack domain value object and RecommendedPack ORM."""

    @staticmethod
    def to_domain(model: RecommendedPackORM) -> RecommendedPack:
        """Convert ORM model to domain value object."""
        if not model:
            return None

        return RecommendedPack(
            id=model.id,
            name=model.name
        )

    @staticmethod
    def to_model(entity: RecommendedPack) -> RecommendedPackORM:
        """Convert domain value object to ORM model."""
        if not entity:
            return None

        return RecommendedPackORM(
            id=entity.id,
            name=entity.name
        )


class LeadMapper:
    """Maps between Lead domain entity and Lead ORM."""

    @staticmethod
    def to_domain(model: LeadORM) -> Lead:
        """Convert ORM model to domain entity."""
        if not model:
            return None

        return Lead(
            id=model.id,
            submission_date=model.submission_date,
            estimated_users=model.estimated_users,
            problem_summary=model.problem_summary,
            maturity_score=model.maturity_score,
            altcha_solution=model.altcha_solution,
            fingerprint_visitor_id=model.fingerprint_visitor_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            contact=ContactMapper.to_domain(model.contact) if model.contact else None,
            company=CompanyMapper.to_domain(model.company) if model.company else None,
            status=LeadStatusMapper.to_domain(model.status) if model.status else None,
            urgency=LeadUrgencyMapper.to_domain(model.urgency) if model.urgency else None,
            recommended_pack=RecommendedPackMapper.to_domain(model.recommended_pack) if model.recommended_pack else None,
            positions=[PositionMapper.to_domain(p) for p in model.positions] if model.positions else [],
            concerns=[ConcernMapper.to_domain(c) for c in model.concerns] if model.concerns else []
        )

    @staticmethod
    def to_model(entity: Lead) -> LeadORM:
        """Convert domain entity to ORM model."""
        if not entity:
            return None

        return LeadORM(
            id=entity.id,
            submission_date=entity.submission_date,
            estimated_users=entity.estimated_users,
            problem_summary=entity.problem_summary,
            maturity_score=entity.maturity_score,
            altcha_solution=entity.altcha_solution,
            fingerprint_visitor_id=entity.fingerprint_visitor_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            contact_id=entity.contact.id if entity.contact else None,
            company_id=entity.company.id if entity.company else None,
            status_id=entity.status.id if entity.status else None,
            urgency_id=entity.urgency.id if entity.urgency else None,
            recommended_pack_id=entity.recommended_pack.id if entity.recommended_pack else None
        )
