"""merge email classification and altcha branches

Revision ID: 534cee69a9a9
Revises: a1b2c3d4e5f6, b0ea83a6aa3e
Create Date: 2025-10-26 11:02:36.437692

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '534cee69a9a9'
down_revision: Union[str, Sequence[str], None] = ('a1b2c3d4e5f6', 'b0ea83a6aa3e')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
