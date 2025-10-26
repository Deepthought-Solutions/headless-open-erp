"""Fingerprint mapper - converts between domain entity and ORM model."""

from domain.entities.fingerprint import Fingerprint
from infrastructure.persistence.models import FingerprintModel as FingerprintORM


class FingerprintMapper:
    """Maps between Fingerprint domain entity and Fingerprint ORM."""

    @staticmethod
    def to_domain(model: FingerprintORM) -> Fingerprint:
        """Convert ORM model to domain entity."""
        if not model:
            return None

        return Fingerprint(
            visitor_id=model.visitorId,
            components=model.components,
            created_at=model.created_at
        )

    @staticmethod
    def to_model(entity: Fingerprint) -> FingerprintORM:
        """Convert domain entity to ORM model."""
        if not entity:
            return None

        return FingerprintORM(
            visitorId=entity.visitor_id,
            components=entity.components,
            created_at=entity.created_at
        )
