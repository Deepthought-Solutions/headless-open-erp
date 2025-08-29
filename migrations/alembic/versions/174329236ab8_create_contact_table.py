"""Create contact table

Revision ID: 174329236ab8
Revises:
Create Date: 2025-07-24 14:50:02.539352

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '174329236ab8'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade the database schema."""
    op.create_table(
        'companies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('employees', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    op.create_table(
        'sectors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    op.create_table(
        'positions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('title')
    )

    op.create_table(
        'concerns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('label', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('label')
    )

    op.create_table(
        'contacts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('message', sa.String(), nullable=True),
        sa.Column('conscent', sa.Boolean(), nullable=False),
        sa.Column('newsletter', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column('company_id', sa.Integer(), sa.ForeignKey('companies.id'), nullable=True),
        sa.Column('sector_id', sa.Integer(), sa.ForeignKey('sectors.id'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contacts_email'), 'contacts', ['email'], unique=False)
    op.create_index(op.f('ix_contacts_id'), 'contacts', ['id'], unique=False)

    op.create_table(
        'contact_positions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), sa.ForeignKey('contacts.id'), nullable=True),
        sa.Column('position_id', sa.Integer(), sa.ForeignKey('positions.id'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'contact_concerns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), sa.ForeignKey('contacts.id'), nullable=True),
        sa.Column('concern_id', sa.Integer(), sa.ForeignKey('concerns.id'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade the database schema."""
    op.drop_table('contact_concerns')
    op.drop_table('contact_positions')
    op.drop_index(op.f('ix_contacts_id'), table_name='contacts')
    op.drop_index(op.f('ix_contacts_email'), table_name='contacts')
    op.drop_table('contacts')
    op.drop_table('concerns')
    op.drop_table('positions')
    op.drop_table('sectors')
    op.drop_table('companies')
