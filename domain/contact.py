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
    visitorId: Optional[str] = None

class LeadUpdateRequest(BaseModel):
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

# Email Account models
class EmailAccountCreate(BaseModel):
    name: str
    imap_host: str
    imap_port: int = 993
    imap_username: str
    imap_password: str
    imap_use_ssl: bool = True

class EmailAccountUpdate(BaseModel):
    name: Optional[str] = None
    imap_host: Optional[str] = None
    imap_port: Optional[int] = None
    imap_username: Optional[str] = None
    imap_password: Optional[str] = None
    imap_use_ssl: Optional[bool] = None

class EmailAccountResponse(BaseModel):
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

# Classified Email models
class ClassifiedEmailCreate(BaseModel):
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
    classification: Optional[str] = None
    emergency_level: Optional[int] = None
    abstract: Optional[str] = None
    lead_id: Optional[int] = None
    change_reason: Optional[str] = None

class EmailClassificationHistoryResponse(BaseModel):
    id: int
    classification: Optional[str]
    emergency_level: Optional[int]
    abstract: Optional[str]
    changed_at: datetime
    change_reason: Optional[str]

    class Config:
        from_attributes = True

class ClassifiedEmailResponse(BaseModel):
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
    classification_history: List[EmailClassificationHistoryResponse] = []

    class Config:
        from_attributes = True
