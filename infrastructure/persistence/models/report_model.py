"""Report ORM model - infrastructure layer."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from infrastructure.database import Base


class ReportModel(Base):
    """SQLAlchemy ORM model for reports - infrastructure concern."""

    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    visitorId = Column(String, ForeignKey("fingerprints.visitorId"), nullable=False)
    page = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))

    fingerprint = relationship("FingerprintModel", backref="reports")
