"""Company DTOs - HTTP response models."""

from pydantic import BaseModel
from typing import Optional


class CompanyResponse(BaseModel):
    """Company response."""
    name: str
    size: Optional[int]

    class Config:
        from_attributes = True
