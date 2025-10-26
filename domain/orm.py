"""
DEPRECATED: This module is deprecated and kept for backward compatibility only.
All ORM models have been moved to infrastructure.persistence.models.

Please update your imports to use:
    from infrastructure.persistence.models import LeadModel, ContactModel, etc.

This file will be removed in a future version.
"""

# Re-export all models for backward compatibility
from infrastructure.persistence.models import (
    ContactModel as Contact,
    CompanyModel as Company,
    PositionModel as Position,
    ConcernModel as Concern,
    SectorModel as Sector,
    LeadStatusModel as LeadStatus,
    LeadUrgencyModel as LeadUrgency,
    RecommendedPackModel as RecommendedPack,
    LeadModel as Lead,
    LeadPositionModel as LeadPosition,
    LeadConcernModel as LeadConcern,
    LeadAttachmentModel as LeadAttachment,
    LeadHistoryModel as LeadHistory,
    LeadModificationLogModel as LeadModificationLog,
    NoteModel as Note,
    NoteReasonModel as NoteReason,
    FingerprintModel as Fingerprint,
    ReportModel as Report,
    EmailAccountModel as EmailAccount,
    ClassifiedEmailModel as ClassifiedEmail,
    EmailClassificationHistoryModel as EmailClassificationHistory,
)

__all__ = [
    'Contact',
    'Company',
    'Position',
    'Concern',
    'Sector',
    'LeadStatus',
    'LeadUrgency',
    'RecommendedPack',
    'Lead',
    'LeadPosition',
    'LeadConcern',
    'LeadAttachment',
    'LeadHistory',
    'LeadModificationLog',
    'Note',
    'NoteReason',
    'Fingerprint',
    'Report',
    'EmailAccount',
    'ClassifiedEmail',
    'EmailClassificationHistory',
]
