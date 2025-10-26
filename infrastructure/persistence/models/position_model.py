"""Position ORM model - infrastructure layer."""

from sqlalchemy import Column, Integer, String
from infrastructure.database import Base


class PositionModel(Base):
    """ORM Model for Position - infrastructure concern."""
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True)
    title = Column(String, unique=True, nullable=False)
