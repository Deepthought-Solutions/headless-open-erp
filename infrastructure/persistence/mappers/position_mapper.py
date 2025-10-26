"""Position mapper - converts between domain entity and ORM model."""

from domain.entities.position import Position
from infrastructure.persistence.models import PositionModel as PositionORM


class PositionMapper:
    """Maps between Position domain entity and Position ORM."""

    @staticmethod
    def to_domain(model: PositionORM) -> Position:
        """Convert ORM model to domain entity."""
        if not model:
            return None

        return Position(
            id=model.id,
            title=model.title
        )

    @staticmethod
    def to_model(entity: Position) -> PositionORM:
        """Convert domain entity to ORM model."""
        if not entity:
            return None

        return PositionORM(
            id=entity.id,
            title=entity.title
        )
