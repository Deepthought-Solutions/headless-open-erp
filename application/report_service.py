import logging
from sqlalchemy.orm import Session
from domain.orm import Report, Fingerprint

logger = logging.getLogger(__name__)

class ReportService:
    def __init__(self, db: Session):
        self.db = db

    def create_report(self, visitor_id: str, page: str):
        try:
            fingerprint = self.db.query(Fingerprint).filter(Fingerprint.visitorId == visitor_id).first()
            if not fingerprint:
                logger.warning(f"Fingerprint not found for visitorId {visitor_id}")
                return None

            report = Report(
                visitorId=visitor_id,
                page=page
            )
            self.db.add(report)
            self.db.commit()
            self.db.refresh(report)
            return report
        except Exception as e:
            logger.exception("Error creating report")
            self.db.rollback()
            raise e
