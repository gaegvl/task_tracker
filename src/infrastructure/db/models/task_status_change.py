from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UUID, String, DateTime, ForeignKey

from src.infrastructure.db.session import Base


class TaskStatusChange(Base):
    __tablename__ = "task_status_changes"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True)
    task_id: Mapped[UUID] = mapped_column(
        UUID, ForeignKey("tasks.id", ondelete="CASCADE")
    )
    from_status: Mapped[str] = mapped_column(String, nullable=False)
    to_state: Mapped[str] = mapped_column(String, nullable=False)
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
