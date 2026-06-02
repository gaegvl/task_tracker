from dataclasses import dataclass
from uuid import UUID, uuid4
from datetime import datetime
from src.application.ports.task_repository import TaskRepositoryPort
from src.application.ports.project_repository import ProjectRepositoryPort
from src.domain.entities.task import Task, TaskStatus


@dataclass(frozen=True)
class CreateTaskCommand:
    title: str
    description: str | None
    project_id: UUID


@dataclass(frozen=True)
class CreateTaskResult:
    id: UUID
    title: str
    status: TaskStatus
    created_at: datetime


class CreateTaskUseCase:
    def __init__(
        self,
        task_repository: TaskRepositoryPort,
        project_repository: ProjectRepositoryPort,
    ) -> None:
        self.task_repository = task_repository
        self.project_repository = project_repository

    async def execute(self, command: CreateTaskCommand) -> CreateTaskResult:
        task = Task(
            id=uuid4(),
            title=command.title,
            description=command.description,
            project_id=command.project_id,
            status=TaskStatus.TODO,
            created_at=datetime.now(),
        )
        await self.project_repository.get_by_id(command.project_id)
        await self.task_repository.add(task=task)
        return CreateTaskResult(
            id=task.id,
            title=task.title,
            status=task.status.value,
            created_at=task.created_at,
        )
