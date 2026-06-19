from src.application.ports.project_repository import ProjectRepositoryPort
from src.application.ports.task_repository import TaskRepositoryPort
from dataclasses import dataclass
from uuid import UUID

from src.application.use_cases.get_project_by_id import CreateProjectResult


@dataclass(frozen=True)
class RestoreProjectCommand:
    project_id: UUID


class RestoreProjectUseCase:
    def __init__(
        self,
        project_repository: ProjectRepositoryPort,
        task_repository: TaskRepositoryPort,
    ) -> None:
        self.project_repository = project_repository
        self.task_repository = task_repository

    async def execute(self, command: RestoreProjectCommand) -> CreateProjectResult:
        project = await self.project_repository.restore(command.project_id)
        await self.task_repository.restore_by_project_id(project.id)
        return CreateProjectResult.from_entity(project)
