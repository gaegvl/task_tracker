from datetime import datetime
from uuid import UUID
from sqlalchemy import String, DateTime, UUID as UUIDType
from sqlalchemy.orm import Mapped, mapped_column
from src.infrastructure.db.session import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(UUIDType, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
