import logging
from sqlalchemy.orm import Session
from domain.orm import Fingerprint

logger = logging.getLogger(__name__)

class FingerprintService:
    def __init__(self, db: Session):
        self.db = db

    def create_fingerprint(self, visitor_id: str, components: dict) -> Fingerprint:
        try:
            fingerprint = Fingerprint(
                visitorId=visitor_id,
                components=components
            )
            self.db.add(fingerprint)
            self.db.commit()
            self.db.refresh(fingerprint)
            return fingerprint
        except Exception as e:
            logger.exception("Error creating fingerprint")
            self.db.rollback()
            raise e
