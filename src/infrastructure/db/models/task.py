from datetime import datetime
from uuid import UUID
from sqlalchemy import ForeignKey, String, DateTime, UUID as UUIDType
from sqlalchemy.orm import Mapped, mapped_column
from src.infrastructure.db.session import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    project_id: Mapped[UUID] = mapped_column(
        UUIDType, ForeignKey("projects.id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
