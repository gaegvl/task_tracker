from dataclasses import dataclass, replace

from uuid import UUID

from src.application.use_cases.get_task_by_id import GetTaskByIdResult
from src.application.ports.task_repository import TaskRepositoryPort
from src.application.ports.project_repository import ProjectRepositoryPort
from src.domain.entities.task import TaskStatus
from src.domain.exceptions import ProjectNotFoundError


@dataclass
class UpdateTaskCommand:
    task_id: UUID
    status: TaskStatus
    title: str | None = None
    description: str | None = None
    project_id: UUID | None = None


class UpdateTaskUseCase:
    def __init__(
        self,
        task_repository: TaskRepositoryPort,
        project_repository: ProjectRepositoryPort,
    ) -> None:
        self.task_repository = task_repository
        self.project_repository = project_repository

    async def execute(self, command: UpdateTaskCommand) -> GetTaskByIdResult:
        task = await self.task_repository.get_by_id(command.task_id)
        if command.project_id:
            project = await self.project_repository.get_by_id(command.project_id)
            if not project:
                raise ProjectNotFoundError(command.project_id)
        updated_task = replace(
            task,
            status=command.status,
            title=command.title or task.title,
            description=command.description or task.description,
            project_id=command.project_id or task.project_id,
        )
        await self.task_repository.update(updated_task)
        return GetTaskByIdResult.from_entity(updated_task)
