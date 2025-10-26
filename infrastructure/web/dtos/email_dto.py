"""Email DTOs - HTTP request/response models."""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class EmailAccountCreate(BaseModel):
    """Email account creation request."""
    name: str
    imap_host: str
    imap_port: int = 993
    imap_username: str
    imap_password: str
    imap_use_ssl: bool = True


class EmailAccountUpdate(BaseModel):
    """Email account update request."""
    name: Optional[str] = None
    imap_host: Optional[str] = None
    imap_port: Optional[int] = None
    imap_username: Optional[str] = None
    imap_password: Optional[str] = None
    imap_use_ssl: Optional[bool] = None


class EmailAccountResponse(BaseModel):
    """Email account response."""
    id: int
    name: str
    imap_host: str
    imap_port: int
    imap_username: str
    imap_use_ssl: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClassifiedEmailCreate(BaseModel):
    """Classified email creation request."""
    email_account_id: int
    imap_id: str
    sender: str
    recipients: str  # Comma-separated
    subject: Optional[str] = None
    email_date: Optional[datetime] = None
    classification: Optional[str] = None
    emergency_level: Optional[int] = None  # 1-5
    abstract: Optional[str] = None  # Max 200 chars
    lead_id: Optional[int] = None


class ClassifiedEmailUpdate(BaseModel):
    """Classified email update request."""
    classification: Optional[str] = None
    emergency_level: Optional[int] = None
    abstract: Optional[str] = None
    lead_id: Optional[int] = None
    change_reason: Optional[str] = None


class EmailClassificationHistoryResponse(BaseModel):
    """Email classification history response."""
    id: int
    classification: Optional[str]
    emergency_level: Optional[int]
    abstract: Optional[str]
    changed_at: datetime
    change_reason: Optional[str]

    class Config:
        from_attributes = True


class ClassifiedEmailResponse(BaseModel):
    """Classified email response."""
    id: int
    email_account_id: int
    imap_id: str
    sender: str
    recipients: str
    subject: Optional[str]
    email_date: Optional[datetime]
    classification: Optional[str]
    emergency_level: Optional[int]
    abstract: Optional[str]
    lead_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClassifiedEmailDetailResponse(ClassifiedEmailResponse):
    """Classified email response with history."""
    classification_history: List[EmailClassificationHistoryResponse] = []

    class Config:
        from_attributes = True
