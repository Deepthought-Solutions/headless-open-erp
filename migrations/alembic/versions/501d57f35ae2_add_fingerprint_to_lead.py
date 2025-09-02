"""add_fingerprint_to_lead

Revision ID: 501d57f35ae2
Revises: 2027b2482496
Create Date: 2025-09-02 09:24:22.387000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '501d57f35ae2'
down_revision: Union[str, Sequence[str], None] = '2027b2482496'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('leads', schema=None) as batch_op:
        batch_op.add_column(sa.Column('fingerprint_visitor_id', sa.String(), nullable=True))
        batch_op.create_foreign_key(
            'fk_leads_fingerprint_visitor_id',
            'fingerprints',
            ['fingerprint_visitor_id'], ['visitorId']
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('leads', schema=None) as batch_op:
        batch_op.drop_constraint('fk_leads_fingerprint_visitor_id', type_='foreignkey')
        batch_op.drop_column('fingerprint_visitor_id')
