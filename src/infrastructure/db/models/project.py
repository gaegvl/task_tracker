from datetime import datetime
from uuid import UUID

from sqlalchemy import UUID as UUIDType
from sqlalchemy import DateTime, String
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
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
