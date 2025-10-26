"""SQLAlchemy implementation of PositionRepository."""

from typing import Optional
from sqlalchemy.orm import Session

from domain.repositories.position_repository import PositionRepository
from domain.entities.position import Position
from infrastructure.persistence.models import PositionModel as PositionORM
from infrastructure.persistence.mappers.position_mapper import PositionMapper


class SqlAlchemyPositionRepository(PositionRepository):
    """Concrete repository implementation using SQLAlchemy."""

    def __init__(self, session: Session):
        self._session = session

    def save(self, position: Position) -> Position:
        """Persist a new position."""
        model = PositionMapper.to_model(position)
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return PositionMapper.to_domain(model)

    def find_by_title(self, title: str) -> Optional[Position]:
        """Find position by title."""
        model = self._session.query(PositionORM).filter(
            PositionORM.title == title
        ).one_or_none()

        return PositionMapper.to_domain(model) if model else None

    def find_by_id(self, position_id: int) -> Optional[Position]:
        """Find position by ID."""
        model = self._session.query(PositionORM).filter(
            PositionORM.id == position_id
        ).one_or_none()

        return PositionMapper.to_domain(model) if model else None
