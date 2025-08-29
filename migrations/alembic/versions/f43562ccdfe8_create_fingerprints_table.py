"""create fingerprints table

Revision ID: f43562ccdfe8
Revises: 856a3e1fb20b
Create Date: 2025-07-26 13:36:00.799912

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f43562ccdfe8'
down_revision: Union[str, Sequence[str], None] = '856a3e1fb20b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from sqlalchemy import JSON

def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'fingerprints',
        sa.Column('visitorId', sa.String(), nullable=False),
        sa.Column('components', JSON, nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('CURRENT_TIMESTAMP'),
            nullable=True
        ),
        sa.PrimaryKeyConstraint('visitorId')
    )
    op.create_index(op.f('ix_fingerprints_visitorId'), 'fingerprints', ['visitorId'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_fingerprints_visitorId'), table_name='fingerprints')
    op.drop_table('fingerprints')
