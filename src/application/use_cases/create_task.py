from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.application.ports.clock import ClockPort
from src.application.ports.id_generator import IdGeneratorPort
from src.application.ports.project_repository import ProjectRepositoryPort
from src.application.ports.task_repository import TaskRepositoryPort
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
        clock: ClockPort,
        id_generator: IdGeneratorPort,
    ) -> None:
        self.task_repository = task_repository
        self.project_repository = project_repository
        self.clock = clock
        self.id_generator = id_generator

    async def execute(self, command: CreateTaskCommand) -> CreateTaskResult:
        task = Task(
            id=self.id_generator.new_id(),
            title=command.title,
            description=command.description,
            project_id=command.project_id,
            status=TaskStatus.TODO,
            created_at=self.clock.now(),
        )
        await self.project_repository.get_by_id(command.project_id)
        await self.task_repository.add(task=task)
        return CreateTaskResult(
            id=task.id,
            title=task.title,
            status=task.status,
            created_at=task.created_at,
        )
