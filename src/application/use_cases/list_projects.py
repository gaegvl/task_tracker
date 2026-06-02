from dataclasses import dataclass
from src.domain.entities.project import Project
from src.application.ports.project_repository import ProjectRepositoryPort


@dataclass(frozen=True)
class ListProjectsCommand:
    limit: int
    offset: int


class ListProjectsUseCase:
    def __init__(self, project_repository: ProjectRepositoryPort) -> None:
        self.project_repository = project_repository

    async def execute(self, command: ListProjectsCommand) -> list[Project]:
        projects = await self.project_repository.list_projects(
            command.limit, command.offset
        )

        return projects
