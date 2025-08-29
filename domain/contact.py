from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class LeadPayload(BaseModel):
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
    lead: LeadPayload
    altcha: str

class ReportRequest(BaseModel):
    altcha: str
    visitorId: str
    page: str

class FingerprintRequest(BaseModel):
    altcha: str
    visitorId: str
    components: dict

# Response models
class ContactResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str]
    job_title: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NoteReasonResponse(BaseModel):
    name: str
    class Config:
        from_attributes = True

class NoteResponse(BaseModel):
    id: int
    note: str
    created_at: datetime
    author_name: str
    reason: NoteReasonResponse

    class Config:
        from_attributes = True

class NoteCreateRequest(BaseModel):
    note: str
    reason: str
    send_to_contact: bool = False
    send_to_recipients: List[EmailStr] = []

class CompanyResponse(BaseModel):
    name: str
    size: Optional[int]

    class Config:
        from_attributes = True

class PositionResponse(BaseModel):
    title: str

    class Config:
        from_attributes = True

class ConcernResponse(BaseModel):
    label: str

    class Config:
        from_attributes = True

class LeadStatusResponse(BaseModel):
    name: str
    class Config:
        from_attributes = True

class LeadUrgencyResponse(BaseModel):
    name: str
    class Config:
        from_attributes = True

class RecommendedPackResponse(BaseModel):
    name: str
    class Config:
        from_attributes = True

class LeadResponse(BaseModel):
    id: int
    submission_date: datetime
    status: LeadStatusResponse
    urgency: LeadUrgencyResponse
    recommended_pack: Optional[RecommendedPackResponse]
    maturity_score: Optional[int]
    potential_score: Optional[int]
    estimated_users: Optional[int]
    problem_summary: Optional[str]

    contact: ContactResponse
    company: CompanyResponse
    positions: List[PositionResponse]
    concerns: List[ConcernResponse]

    class Config:
        from_attributes = True
