"""SQLAlchemy implementation of FingerprintRepository."""

from typing import Optional
from sqlalchemy.orm import Session

from domain.repositories.fingerprint_repository import FingerprintRepository
from domain.entities.fingerprint import Fingerprint
from infrastructure.persistence.models import FingerprintModel as FingerprintORM
from infrastructure.persistence.mappers.fingerprint_mapper import FingerprintMapper


class SqlAlchemyFingerprintRepository(FingerprintRepository):
    """Concrete repository implementation using SQLAlchemy."""

    def __init__(self, session: Session):
        self._session = session

    def save(self, fingerprint: Fingerprint) -> Fingerprint:
        """Persist a new or updated fingerprint."""
        # Check if fingerprint already exists in the database
        existing_model = self._session.query(FingerprintORM).filter(
            FingerprintORM.visitorId == fingerprint.visitor_id
        ).one_or_none()

        if existing_model:
            # Update existing record
            existing_model.components = fingerprint.components
            existing_model.created_at = fingerprint.created_at
            model = existing_model
        else:
            # Create new record
            model = FingerprintMapper.to_model(fingerprint)
            self._session.add(model)

        self._session.commit()
        self._session.refresh(model)
        return FingerprintMapper.to_domain(model)

    def find_by_visitor_id(self, visitor_id: str) -> Optional[Fingerprint]:
        """Find fingerprint by visitor ID."""
        model = self._session.query(FingerprintORM).filter(
            FingerprintORM.visitorId == visitor_id
        ).one_or_none()

        return FingerprintMapper.to_domain(model) if model else None

    def exists(self, visitor_id: str) -> bool:
        """Check if fingerprint exists."""
        count = self._session.query(FingerprintORM).filter(
            FingerprintORM.visitorId == visitor_id
        ).count()
        return count > 0
