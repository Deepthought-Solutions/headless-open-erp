"""Note DTOs - HTTP request/response models."""

from pydantic import BaseModel, EmailStr
from typing import List
from datetime import datetime


class NoteReasonResponse(BaseModel):
    """Note reason response."""
    name: str

    class Config:
        from_attributes = True


class NoteResponse(BaseModel):
    """Note response."""
    id: int
    note: str
    created_at: datetime
    author_name: str
    reason: NoteReasonResponse

    class Config:
        from_attributes = True


class NoteCreateRequest(BaseModel):
    """Note creation request."""
    note: str
    reason: str
    send_to_contact: bool = False
    send_to_recipients: List[EmailStr] = []
