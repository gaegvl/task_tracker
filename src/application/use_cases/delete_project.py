from dataclasses import dataclass
from uuid import UUID
from src.application.ports.project_repository import ProjectRepositoryPort
from src.application.ports.task_repository import TaskRepositoryPort
from src.domain.exceptions import ProjectHasTasksError


@dataclass(frozen=True)
class DeleteProjectCommand:
    id: UUID


class DeleteProjectUseCase:
    def __init__(
        self,
        project_repository: ProjectRepositoryPort,
        task_repository: TaskRepositoryPort,
    ) -> None:
        self.project_repository = project_repository
        self.task_repository = task_repository

    async def execute(self, command: DeleteProjectCommand) -> None:
        project = await self.project_repository.get_by_id(command.id)
        if await self.task_repository.exists_by_project_id(project.id):
            raise ProjectHasTasksError(project.id)
        await self.project_repository.delete(project.id)
