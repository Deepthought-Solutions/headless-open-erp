"""add email classification tables

Revision ID: a1b2c3d4e5f6
Revises: c69042aa4359
Create Date: 2025-10-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'c69042aa4359'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create email_accounts table
    op.create_table('email_accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('imap_host', sa.String(), nullable=False),
        sa.Column('imap_port', sa.Integer(), nullable=False),
        sa.Column('imap_username', sa.String(), nullable=False),
        sa.Column('imap_password', sa.String(), nullable=False),
        sa.Column('imap_use_ssl', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_email_accounts_id'), 'email_accounts', ['id'], unique=False)

    # Create classified_emails table
    op.create_table('classified_emails',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email_account_id', sa.Integer(), nullable=False),
        sa.Column('imap_id', sa.String(), nullable=False),
        sa.Column('sender', sa.String(), nullable=False),
        sa.Column('recipients', sa.String(), nullable=False),
        sa.Column('subject', sa.String(), nullable=True),
        sa.Column('email_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('classification', sa.String(), nullable=True),
        sa.Column('emergency_level', sa.Integer(), nullable=True),
        sa.Column('abstract', sa.String(200), nullable=True),
        sa.Column('lead_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.ForeignKeyConstraint(['email_account_id'], ['email_accounts.id'], ),
        sa.ForeignKeyConstraint(['lead_id'], ['leads.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_classified_emails_id'), 'classified_emails', ['id'], unique=False)

    # Create email_classification_history table
    op.create_table('email_classification_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('classified_email_id', sa.Integer(), nullable=False),
        sa.Column('classification', sa.String(), nullable=True),
        sa.Column('emergency_level', sa.Integer(), nullable=True),
        sa.Column('abstract', sa.String(200), nullable=True),
        sa.Column('changed_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('change_reason', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['classified_email_id'], ['classified_emails.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_email_classification_history_id'), 'email_classification_history', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_email_classification_history_id'), table_name='email_classification_history')
    op.drop_table('email_classification_history')
    op.drop_index(op.f('ix_classified_emails_id'), table_name='classified_emails')
    op.drop_table('classified_emails')
    op.drop_index(op.f('ix_email_accounts_id'), table_name='email_accounts')
    op.drop_table('email_accounts')
