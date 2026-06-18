from dataclasses import dataclass, replace
from datetime import datetime
from uuid import UUID
from src.domain.exceptions import InvalidProjectNameError


@dataclass
class Project:
    id: UUID
    name: str
    description: str | None
    created_at: datetime
    deleted_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvalidProjectNameError("Name cannot be empty")
        if len(self.name.strip()) < 3:
            raise InvalidProjectNameError("Name must be at least 3 characters long")

    def mark_deleted(self, at: datetime) -> Project:
        return replace(self, deleted_at=at)
