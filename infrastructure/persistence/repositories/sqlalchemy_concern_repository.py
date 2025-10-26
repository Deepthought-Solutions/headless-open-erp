"""SQLAlchemy implementation of ConcernRepository."""

from typing import Optional
from sqlalchemy.orm import Session

from domain.repositories.concern_repository import ConcernRepository
from domain.entities.concern import Concern
from infrastructure.persistence.models import ConcernModel as ConcernORM
from infrastructure.persistence.mappers.concern_mapper import ConcernMapper


class SqlAlchemyConcernRepository(ConcernRepository):
    """Concrete repository implementation using SQLAlchemy."""

    def __init__(self, session: Session):
        self._session = session

    def save(self, concern: Concern) -> Concern:
        """Persist a new concern."""
        model = ConcernMapper.to_model(concern)
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return ConcernMapper.to_domain(model)

    def find_by_label(self, label: str) -> Optional[Concern]:
        """Find concern by label."""
        model = self._session.query(ConcernORM).filter(
            ConcernORM.label == label
        ).one_or_none()

        return ConcernMapper.to_domain(model) if model else None

    def find_by_id(self, concern_id: int) -> Optional[Concern]:
        """Find concern by ID."""
        model = self._session.query(ConcernORM).filter(
            ConcernORM.id == concern_id
        ).one_or_none()

        return ConcernMapper.to_domain(model) if model else None
