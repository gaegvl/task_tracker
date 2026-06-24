"""add project deleted_at

Revision ID: 0b593a56ccb0
Revises: a51936122df4
Create Date: 2026-06-16 14:28:11.907478

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0b593a56ccb0"
down_revision: str | Sequence[str] | None = "a51936122df4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "projects", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("projects", "deleted_at")
