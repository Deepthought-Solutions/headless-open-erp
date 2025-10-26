"""Repository implementations - infrastructure layer implements domain interfaces."""

from .sqlalchemy_fingerprint_repository import SqlAlchemyFingerprintRepository
from .sqlalchemy_report_repository import SqlAlchemyReportRepository
from .sqlalchemy_note_repository import SqlAlchemyNoteRepository
from .sqlalchemy_contact_repository import SqlAlchemyContactRepository
from .sqlalchemy_company_repository import SqlAlchemyCompanyRepository
from .sqlalchemy_position_repository import SqlAlchemyPositionRepository
from .sqlalchemy_concern_repository import SqlAlchemyConcernRepository
from .sqlalchemy_lead_repository import SqlAlchemyLeadRepository
from .sqlalchemy_email_repository import SqlAlchemyEmailAccountRepository, SqlAlchemyClassifiedEmailRepository

__all__ = [
    'SqlAlchemyFingerprintRepository',
    'SqlAlchemyReportRepository',
    'SqlAlchemyNoteRepository',
    'SqlAlchemyContactRepository',
    'SqlAlchemyCompanyRepository',
    'SqlAlchemyPositionRepository',
    'SqlAlchemyConcernRepository',
    'SqlAlchemyLeadRepository',
    'SqlAlchemyEmailAccountRepository',
    'SqlAlchemyClassifiedEmailRepository',
]
