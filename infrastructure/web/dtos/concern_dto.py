"""Concern DTOs - HTTP response models."""

from pydantic import BaseModel


class ConcernResponse(BaseModel):
    """Concern response."""
    label: str

    class Config:
        from_attributes = True
