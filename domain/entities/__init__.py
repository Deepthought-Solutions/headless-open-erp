"""Domain entities - pure business objects with no framework dependencies."""

from .contact import Contact
from .company import Company
from .lead import Lead, LeadStatus, LeadUrgency, RecommendedPack
from .position import Position
from .concern import Concern
from .note import Note, NoteReason
from .fingerprint import Fingerprint
from .report import Report
from .email import EmailAccount, ClassifiedEmail, EmailClassificationHistory

__all__ = [
    'Contact',
    'Company',
    'Lead',
    'LeadStatus',
    'LeadUrgency',
    'RecommendedPack',
    'Position',
    'Concern',
    'Note',
    'NoteReason',
    'Fingerprint',
    'Report',
    'EmailAccount',
    'ClassifiedEmail',
    'EmailClassificationHistory',
]
