from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum
from uuid import UUID

from src.domain.exceptions import (
    InvalidTaskStatusTransitionError,
    InvalidTaskTitleError,
)


class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


@dataclass
class Task:
    id: UUID
    title: str
    description: str | None
    project_id: UUID
    status: TaskStatus
    created_at: datetime
    deleted_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise InvalidTaskTitleError("Title cannot be empty")
        if len(self.title.strip()) < 3:
            raise InvalidTaskTitleError("Title must be at least 3 characters long")

    def _is_valid_status_transition(
        self, current_status: TaskStatus, new_status: TaskStatus
    ) -> bool:
        return (
            current_status == TaskStatus.TODO
            and new_status == TaskStatus.IN_PROGRESS
            or current_status == TaskStatus.IN_PROGRESS
            and new_status == TaskStatus.DONE
            or current_status == TaskStatus.IN_PROGRESS
            and new_status == TaskStatus.TODO
            or current_status == new_status
        )

    def with_status(self, new_status: TaskStatus) -> Task:
        if not self._is_valid_status_transition(self.status, new_status):
            raise InvalidTaskStatusTransitionError(self.status, new_status)
        return replace(self, status=new_status)

    def apply_updates(
        self,
        *,
        status: TaskStatus,
        title: str | None = None,
        description: str | None = None,
        project_id: UUID | None = None,
    ) -> Task:
        updated = self.with_status(status)
        return replace(
            updated,
            title=title or self.title,
            description=description or self.description,
            project_id=project_id or self.project_id,
        )

    def mark_deleted(self, at: datetime) -> Task:
        return replace(self, deleted_at=at)

    def restore(self) -> Task:
        return replace(self, deleted_at=None)
