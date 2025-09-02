"""add_altcha_to_lead

Revision ID: b0ea83a6aa3e
Revises: 501d57f35ae2
Create Date: 2025-09-02 09:31:13.200000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b0ea83a6aa3e'
down_revision: Union[str, Sequence[str], None] = '501d57f35ae2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('leads', schema=None) as batch_op:
        batch_op.add_column(sa.Column('altcha_solution', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('leads', schema=None) as batch_op:
        batch_op.drop_column('altcha_solution')
