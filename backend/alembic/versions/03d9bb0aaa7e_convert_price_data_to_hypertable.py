"""convert price_data to hypertable

Revision ID: 03d9bb0aaa7e
Revises: e4915beb48c3
Create Date: 2026-03-27 01:02:27.359510
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers
revision: str = '03d9bb0aaa7e'
down_revision: Union[str, None] = 'e4915beb48c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("SELECT create_hypertable('price_data', 'time');")
    pass


def downgrade() -> None:
    pass
