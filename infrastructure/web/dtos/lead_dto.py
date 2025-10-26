"""Lead DTOs - HTTP request/response models."""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class LeadPayload(BaseModel):
    """Lead creation payload."""
    name: str
    email: EmailStr
    phone: Optional[str] = None
    job_title: Optional[str] = None
    company_name: str
    company_size: Optional[int] = None
    positions: List[str]
    concerns: List[str]
    problem_summary: Optional[str] = None
    estimated_users: Optional[int] = None
    urgency: str
    conscent: bool


class LeadRequest(BaseModel):
    """Lead creation request with ALTCHA verification."""
    lead: LeadPayload
    altcha: str
    visitorId: Optional[str] = None


class LeadUpdateRequest(BaseModel):
    """Lead update request."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    company_size: Optional[int] = None
    positions: Optional[List[str]] = None
    concerns: Optional[List[str]] = None
    problem_summary: Optional[str] = None
    estimated_users: Optional[int] = None
    urgency: Optional[str] = None
    conscent: Optional[bool] = None
    altcha: str
    visitorId: str


class LeadStatusResponse(BaseModel):
    """Lead status response."""
    name: str

    class Config:
        from_attributes = True


class LeadUrgencyResponse(BaseModel):
    """Lead urgency response."""
    name: str

    class Config:
        from_attributes = True


class RecommendedPackResponse(BaseModel):
    """Recommended pack response."""
    name: str

    class Config:
        from_attributes = True


class LeadResponse(BaseModel):
    """Lead response with all relationships."""
    id: int
    submission_date: datetime
    status: LeadStatusResponse
    urgency: LeadUrgencyResponse
    recommended_pack: Optional[RecommendedPackResponse]
    maturity_score: Optional[int]
    potential_score: Optional[int]
    estimated_users: Optional[int]
    problem_summary: Optional[str]

    # Import here to avoid circular dependency
    contact: 'ContactResponse'
    company: 'CompanyResponse'
    positions: List['PositionResponse']
    concerns: List['ConcernResponse']

    class Config:
        from_attributes = True


# Import here to avoid circular dependency
from .contact_dto import ContactResponse
from .company_dto import CompanyResponse
from .position_dto import PositionResponse
from .concern_dto import ConcernResponse

LeadResponse.model_rebuild()
