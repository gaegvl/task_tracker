"""empty message

Revision ID: a51936122df4
Revises: 26f61f6479fa
Create Date: 2026-06-15 18:32:02.060095

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a51936122df4"
down_revision: Union[str, Sequence[str], None] = "26f61f6479fa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "tasks", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("tasks", "deleted_at")
