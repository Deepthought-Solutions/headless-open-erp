import logging
from datetime import datetime

from domain.repositories.report_repository import ReportRepository
from domain.repositories.fingerprint_repository import FingerprintRepository
from domain.entities.report import Report

logger = logging.getLogger(__name__)

class ReportService:
    """Application service for report operations - uses repository pattern."""

    def __init__(
        self,
        report_repository: ReportRepository,
        fingerprint_repository: FingerprintRepository
    ):
        self._report_repo = report_repository
        self._fingerprint_repo = fingerprint_repository

    def create_report(self, visitor_id: str, page: str):
        """Create a report for a visitor's page visit."""
        try:
            # Check if fingerprint exists
            if not self._fingerprint_repo.exists(visitor_id):
                logger.warning(f"Fingerprint not found for visitorId {visitor_id}")
                return None

            # Create report domain entity
            report = Report(
                id=None,
                visitor_id=visitor_id,
                page=page,
                created_at=datetime.now()
            )
            return self._report_repo.save(report)
        except Exception as e:
            logger.exception("Error creating report")
            raise e
