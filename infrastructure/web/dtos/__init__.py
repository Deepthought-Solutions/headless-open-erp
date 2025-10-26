"""HTTP DTOs - infrastructure concern, Pydantic models for FastAPI."""

from .lead_dto import (
    LeadPayload,
    LeadRequest,
    LeadUpdateRequest,
    LeadResponse,
    LeadStatusResponse,
    LeadUrgencyResponse,
    RecommendedPackResponse,
)
from .contact_dto import ContactResponse
from .company_dto import CompanyResponse
from .position_dto import PositionResponse
from .concern_dto import ConcernResponse
from .note_dto import NoteResponse, NoteReasonResponse, NoteCreateRequest
from .fingerprint_dto import FingerprintRequest
from .report_dto import ReportRequest
from .email_dto import (
    EmailAccountCreate,
    EmailAccountUpdate,
    EmailAccountResponse,
    ClassifiedEmailCreate,
    ClassifiedEmailUpdate,
    ClassifiedEmailResponse,
    ClassifiedEmailDetailResponse,
    EmailClassificationHistoryResponse,
)

__all__ = [
    'LeadPayload',
    'LeadRequest',
    'LeadUpdateRequest',
    'LeadResponse',
    'LeadStatusResponse',
    'LeadUrgencyResponse',
    'RecommendedPackResponse',
    'ContactResponse',
    'CompanyResponse',
    'PositionResponse',
    'ConcernResponse',
    'NoteResponse',
    'NoteReasonResponse',
    'NoteCreateRequest',
    'FingerprintRequest',
    'ReportRequest',
    'EmailAccountCreate',
    'EmailAccountUpdate',
    'EmailAccountResponse',
    'ClassifiedEmailCreate',
    'ClassifiedEmailUpdate',
    'ClassifiedEmailResponse',
    'ClassifiedEmailDetailResponse',
    'EmailClassificationHistoryResponse',
]
