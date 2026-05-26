from dataclasses import dataclass, replace

from uuid import UUID

from src.application.use_cases.get_task_by_id import GetTaskByIdResult
from src.domain.exceptions import TaskNotFoundError
from src.application.ports.task_repository import TaskRepositoryPort
from src.domain.entities.task import TaskStatus


@dataclass
class UpdateTaskCommand:
    task_id: UUID
    status: TaskStatus
    title: str | None = None
    description: str | None = None
    project_id: UUID | None = None


class UpdateTaskUseCase:
    def __init__(self, task_repository: TaskRepositoryPort) -> None:
        self.task_repository = task_repository

    async def execute(self, command: UpdateTaskCommand) -> GetTaskByIdResult:
        task = await self.task_repository.get_by_id(command.task_id)
        if task is None:
            raise TaskNotFoundError(command.task_id)

        updated_task = replace(
            task,
            status=command.status,
            title=command.title or task.title,
            description=command.description or task.description,
            project_id=command.project_id or task.project_id,
        )
        await self.task_repository.update(updated_task)
        return GetTaskByIdResult.from_entity(updated_task)
