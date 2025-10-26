"""Company ORM model - infrastructure layer."""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from infrastructure.database import Base


class CompanyModel(Base):
    """ORM Model for Company - infrastructure concern."""
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    size = Column(Integer, nullable=True)

    leads = relationship("LeadModel", back_populates="company")
