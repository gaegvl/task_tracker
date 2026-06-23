from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

from src.domain.entities.task import TaskStatus


class ListTaskStatusHistoryParams(BaseModel):
    limit: int = Field(ge=1, le=100, default=10)
    offset: int = Field(ge=0, default=0)


class TaskStatusChangeResponse(BaseModel):
    id: UUID
    task_id: UUID
    from_status: TaskStatus
    to_state: TaskStatus
    changed_at: datetime
