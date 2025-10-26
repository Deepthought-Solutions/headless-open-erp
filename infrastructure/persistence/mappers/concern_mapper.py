"""Concern mapper - converts between domain entity and ORM model."""

from domain.entities.concern import Concern
from infrastructure.persistence.models import ConcernModel as ConcernORM


class ConcernMapper:
    """Maps between Concern domain entity and Concern ORM."""

    @staticmethod
    def to_domain(model: ConcernORM) -> Concern:
        """Convert ORM model to domain entity."""
        if not model:
            return None

        return Concern(
            id=model.id,
            label=model.label
        )

    @staticmethod
    def to_model(entity: Concern) -> ConcernORM:
        """Convert domain entity to ORM model."""
        if not entity:
            return None

        return ConcernORM(
            id=entity.id,
            label=entity.label
        )
