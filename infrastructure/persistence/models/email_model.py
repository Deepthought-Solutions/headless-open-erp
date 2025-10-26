"""Email ORM models - infrastructure layer."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from infrastructure.database import Base


class EmailAccountModel(Base):
    """ORM Model for Email Account - infrastructure concern."""
    __tablename__ = 'email_accounts'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # Identifier/label for the account
    imap_host = Column(String, nullable=False)
    imap_port = Column(Integer, nullable=False, default=993)
    imap_username = Column(String, nullable=False)
    imap_password = Column(String, nullable=False)  # Consider encrypting in production
    imap_use_ssl = Column(Integer, nullable=False, default=1)  # SQLite compatible boolean
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    classified_emails = relationship("ClassifiedEmailModel", back_populates="email_account")


class ClassifiedEmailModel(Base):
    """ORM Model for Classified Email - infrastructure concern."""
    __tablename__ = 'classified_emails'

    id = Column(Integer, primary_key=True, index=True)

    # IMAP identification
    email_account_id = Column(Integer, ForeignKey('email_accounts.id'), nullable=False)
    imap_id = Column(String, nullable=False)

    # Email metadata
    sender = Column(String, nullable=False)
    recipients = Column(String, nullable=False)  # Comma-separated list
    subject = Column(String, nullable=True)
    email_date = Column(DateTime(timezone=True), nullable=True)

    # LLM classification
    classification = Column(String, nullable=True)  # Free text
    emergency_level = Column(Integer, nullable=True)  # 1-5 scale
    abstract = Column(String(200), nullable=True)  # 200 char limit

    # Optional lead relationship
    lead_id = Column(Integer, ForeignKey('leads.id'), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    email_account = relationship("EmailAccountModel", back_populates="classified_emails")
    lead = relationship("LeadModel")
    classification_history = relationship("EmailClassificationHistoryModel", back_populates="classified_email")


class EmailClassificationHistoryModel(Base):
    """ORM Model for Email Classification History - infrastructure concern."""
    __tablename__ = 'email_classification_history'

    id = Column(Integer, primary_key=True, index=True)
    classified_email_id = Column(Integer, ForeignKey('classified_emails.id'), nullable=False)

    # Previous classification values
    classification = Column(String, nullable=True)
    emergency_level = Column(Integer, nullable=True)
    abstract = Column(String(200), nullable=True)

    # Change metadata
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
    change_reason = Column(String, nullable=True)

    classified_email = relationship("ClassifiedEmailModel", back_populates="classification_history")
