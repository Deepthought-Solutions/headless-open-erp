"""Repository interfaces - domain defines what it needs, infrastructure implements how."""

from .lead_repository import LeadRepository
from .contact_repository import ContactRepository
from .company_repository import CompanyRepository
from .position_repository import PositionRepository
from .concern_repository import ConcernRepository
from .note_repository import NoteRepository
from .fingerprint_repository import FingerprintRepository
from .report_repository import ReportRepository
from .email_repository import EmailAccountRepository, ClassifiedEmailRepository

__all__ = [
    'LeadRepository',
    'ContactRepository',
    'CompanyRepository',
    'PositionRepository',
    'ConcernRepository',
    'NoteRepository',
    'FingerprintRepository',
    'ReportRepository',
    'EmailAccountRepository',
    'ClassifiedEmailRepository',
]
