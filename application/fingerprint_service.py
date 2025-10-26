import logging
from datetime import datetime

from domain.repositories.fingerprint_repository import FingerprintRepository
from domain.entities.fingerprint import Fingerprint

logger = logging.getLogger(__name__)

class FingerprintService:
    """Application service for fingerprint operations - uses repository pattern."""

    def __init__(self, fingerprint_repository: FingerprintRepository):
        self._fingerprint_repo = fingerprint_repository

    def create_fingerprint(self, visitor_id: str, components: dict) -> Fingerprint:
        """Create or update a fingerprint."""
        try:
            # Check if fingerprint already exists
            existing = self._fingerprint_repo.find_by_visitor_id(visitor_id)

            if existing:
                # Update existing fingerprint
                existing.components = components
                return self._fingerprint_repo.save(existing)
            else:
                # Create new fingerprint domain entity
                fingerprint = Fingerprint(
                    visitor_id=visitor_id,
                    components=components,
                    created_at=datetime.now()
                )
                return self._fingerprint_repo.save(fingerprint)
        except Exception as e:
            logger.exception("Error creating fingerprint")
            raise e
