"""Position DTOs - HTTP response models."""

from pydantic import BaseModel


class PositionResponse(BaseModel):
    """Position response."""
    title: str

    class Config:
        from_attributes = True
