from dataclasses import dataclass, replace
from uuid import UUID
from src.application.ports.project_repository import ProjectRepositoryPort
from src.application.use_cases.create_project import CreateProjectResult


@dataclass(frozen=True)
class UpdateProjectCommand:
    id: UUID
    name: str
    description: str | None


class UpdateProjectUseCase:
    def __init__(self, project_repository: ProjectRepositoryPort) -> None:
        self.project_repository = project_repository

    async def execute(self, command: UpdateProjectCommand) -> CreateProjectResult:
        project = await self.project_repository.get_by_id(command.id)
        updated_project = replace(
            project,
            name=command.name or project.name,
            description=command.description or project.description,
        )
        await self.project_repository.update(project=updated_project)
        return CreateProjectResult.from_entity(updated_project)
