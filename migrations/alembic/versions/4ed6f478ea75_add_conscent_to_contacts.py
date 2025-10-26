"""add_conscent_to_contacts

Revision ID: 4ed6f478ea75
Revises: 534cee69a9a9
Create Date: 2025-10-26 13:21:12.894199

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4ed6f478ea75'
down_revision: Union[str, Sequence[str], None] = '534cee69a9a9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add conscent column to contacts table with data migration."""
    # Add the column with a default value
    op.add_column('contacts', sa.Column('conscent', sa.Boolean(), nullable=True))

    # Migrate data: set conscent to True for all existing contacts that have associated leads
    # (assuming they gave consent when submitting the lead form)
    op.execute("""
        UPDATE contacts
        SET conscent = TRUE
        WHERE id IN (SELECT DISTINCT contact_id FROM leads)
    """)

    # Set any remaining contacts to False
    op.execute("""
        UPDATE contacts
        SET conscent = FALSE
        WHERE conscent IS NULL
    """)

    # Make the column non-nullable now that all values are set
    with op.batch_alter_table('contacts', schema=None) as batch_op:
        batch_op.alter_column('conscent', nullable=False, server_default='0')


def downgrade() -> None:
    """Remove conscent column from contacts table."""
    op.drop_column('contacts', 'conscent')
