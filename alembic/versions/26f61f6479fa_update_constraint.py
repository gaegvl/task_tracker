"""empty message

Revision ID: 26f61f6479fa
Revises: 8dc7a4942e59
Create Date: 2026-06-01 16:13:21.840272

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "26f61f6479fa"
down_revision: Union[str, Sequence[str], None] = "8dc7a4942e59"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint("fk_task_project_id_projects", "tasks", type_="foreignkey")
    op.create_foreign_key(
        "fk_task_project_id_projects",
        "tasks",
        "projects",
        ["project_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("fk_task_project_id_projects", "tasks", type_="foreignkey")
    op.create_foreign_key(
        "fk_task_project_id_projects", "tasks", "projects", ["project_id"], ["id"]
    )
