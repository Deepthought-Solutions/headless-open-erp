import logging
from sqlalchemy.orm import Session
from domain.orm import Fingerprint

logger = logging.getLogger(__name__)

class FingerprintService:
    def __init__(self, db: Session):
        self.db = db

    def create_fingerprint(self, visitor_id: str, components: dict) -> Fingerprint:
        try:
            # Check if fingerprint already exists
            fingerprint = self.db.query(Fingerprint).filter(Fingerprint.visitorId == visitor_id).first()

            if fingerprint:
                # Update existing fingerprint
                fingerprint.components = components
            else:
                # Create new fingerprint
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
