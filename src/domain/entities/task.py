from dataclasses import dataclass
from enum import Enum
from datetime import datetime
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

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise InvalidTaskTitleError("Title cannot be empty")
        if len(self.title.strip()) < 3:
            raise InvalidTaskTitleError("Title must be at least 3 characters long")

    def change_status(self, new_status: TaskStatus) -> None:
        if (
            self.status == TaskStatus.TODO
            and new_status == TaskStatus.IN_PROGRESS
            or self.status == TaskStatus.IN_PROGRESS
            and new_status == TaskStatus.DONE
            or self.status == TaskStatus.IN_PROGRESS
            and new_status == TaskStatus.TODO
            or self.status == new_status
        ):
            return
        raise InvalidTaskStatusTransitionError(self.status, new_status)
