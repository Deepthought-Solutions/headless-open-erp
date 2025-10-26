"""Contact DTOs - HTTP response models."""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class ContactResponse(BaseModel):
    """Contact response."""
    id: int
    name: str
    email: EmailStr
    phone: Optional[str]
    job_title: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
