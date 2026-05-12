from uuid import UUID
from pydantic import BaseModel
from datetime import datetime
from src.domain.entities.task import TaskStatus


class CreateTaskRequest(BaseModel):
    title: str
    description: str | None = None
    project_id: UUID


class CreateTaskResponse(BaseModel):
    id: UUID
    title: str
    status: TaskStatus
    created_at: datetime


class TaskResponse(CreateTaskResponse):
    description: str | None
    project_id: UUID
