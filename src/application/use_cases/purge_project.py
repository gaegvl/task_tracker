from dataclasses import dataclass
from uuid import UUID

from src.application.ports.project_repository import ProjectRepositoryPort
from src.application.ports.task_repository import TaskRepositoryPort
from src.domain.exceptions import ProjectHasTasksError


@dataclass(frozen=True)
class PurgeProjectCommand:
    project_id: UUID


class PurgeProjectUseCase:
    def __init__(
        self,
        project_repository: ProjectRepositoryPort,
        task_repository: TaskRepositoryPort,
    ) -> None:
        self.project_repository = project_repository
        self.task_repository = task_repository

    async def execute(self, command: PurgeProjectCommand) -> None:
        project = await self.project_repository.find_soft_deleted(command.project_id)
        if await self.task_repository.exists_by_project_id(command.project_id):
            raise ProjectHasTasksError(command.project_id)
        await self.task_repository.purge_by_project_id(command.project_id)
        await self.project_repository.purge(project)
