from datetime import datetime
from uuid import UUID

from sqlalchemy import UUID as UUIDType
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.session import Base


class TaskStatusChange(Base):
    __tablename__ = "task_status_changes"

    id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True)
    task_id: Mapped[UUID] = mapped_column(
        UUIDType, ForeignKey("tasks.id", ondelete="CASCADE")
    )
    from_status: Mapped[str] = mapped_column(String, nullable=False)
    to_state: Mapped[str] = mapped_column(String, nullable=False)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
