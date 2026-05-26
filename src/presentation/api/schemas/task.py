from uuid import UUID
from pydantic import BaseModel, Field
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


class ListTasksParams(BaseModel):
    project_id: UUID
    status: TaskStatus | None = None
    limit: int = Field(ge=1, le=100, default=20)
    offset: int = Field(ge=0, default=0)
