from dataclasses import dataclass
from uuid import UUID

from src.application.ports.project_repository import ProjectRepositoryPort
from src.application.use_cases.create_project import CreateProjectResult


@dataclass(frozen=True)
class GetProjectByIdCommand:
    id: UUID


class GetProjectByIdUseCase:
    def __init__(self, project_repository: ProjectRepositoryPort) -> None:
        self.project_repositoty = project_repository

    async def execute(self, command: GetProjectByIdCommand) -> CreateProjectResult:
        project = await self.project_repositoty.get_by_id(command.id)
        return CreateProjectResult.from_entity(project=project)
