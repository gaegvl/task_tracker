from dataclasses import dataclass
from uuid import UUID
from datetime import datetime

from src.domain.entities.task import TaskStatus


@dataclass(frozen=True)
class TaskStatusChange:
    id: UUID
    task_id: UUID
    from_status: TaskStatus
    to_state: TaskStatus
    changed_at: datetime
