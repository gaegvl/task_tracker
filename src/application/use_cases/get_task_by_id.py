from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from src.domain.entities.task import TaskStatus, Task
from src.application.ports.task_repository import TaskRepositoryPort
from src.domain.exceptions import TaskNotFoundError


@dataclass(frozen=True)
class GetTaskByIdCommand:
    id: UUID


@dataclass(frozen=True)
class GetTaskByIdResult:
    id: UUID
    title: str
    description: str | None
    project_id: UUID
    status: TaskStatus
    created_at: datetime

    @classmethod
    def from_entity(cls, task: Task) -> "GetTaskByIdResult":
        return cls(
            id=task.id,
            title=task.title,
            description=task.description,
            project_id=task.project_id,
            status=task.status,
            created_at=task.created_at,
        )


class GetTaskByIdUseCase:
    def __init__(self, task_repository: TaskRepositoryPort) -> None:
        self.task_repository = task_repository

    async def execute(self, command: GetTaskByIdCommand) -> GetTaskByIdResult:
        task = await self.task_repository.get_by_id(command.id)
        if task is None:
            raise TaskNotFoundError(command.id)
        return GetTaskByIdResult.from_entity(task)
