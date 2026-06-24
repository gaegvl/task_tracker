from dataclasses import dataclass
from uuid import UUID

from src.application.ports.project_repository import ProjectRepositoryPort
from src.application.ports.task_repository import TaskRepositoryPort
from src.application.use_cases.get_task_by_id import GetTaskByIdResult


@dataclass(frozen=True)
class RestoreTaskCommand:
    task_id: UUID


class RestoreTaskUseCase:
    def __init__(
        self,
        task_repository: TaskRepositoryPort,
        project_repository: ProjectRepositoryPort,
    ) -> None:
        self.task_repository = task_repository
        self.project_repository = project_repository

    async def execute(self, command: RestoreTaskCommand) -> GetTaskByIdResult:
        task = await self.task_repository.find_soft_deleted(command.task_id)
        await self.project_repository.get_by_id(task.project_id)
        task = await self.task_repository.restore(task)
        return GetTaskByIdResult.from_entity(task)
