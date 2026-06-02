from uuid import UUID
from src.domain.exceptions import ProjectNotFoundError
from src.domain.entities.project import Project
from src.application.ports.project_repository import ProjectRepositoryPort


class InMemoryProjectRepository(ProjectRepositoryPort):
    def __init__(self) -> None:
        self.in_memory_project_repository: dict[UUID, Project] = {}

    async def add(self, project: Project) -> None:
        self.in_memory_project_repository[project.id] = project

    async def get_by_id(self, project_id: UUID) -> Project:
        project = self.in_memory_project_repository.get(project_id)
        if not project:
            raise ProjectNotFoundError(project_id)
        return project

    async def update(self, project: Project) -> None:
        self.in_memory_project_repository[project.id] = project

    async def list_projects(self, limit: int, offset: int) -> list[Project]:
        return list(self.in_memory_project_repository.values())[offset : offset + limit]

    async def delete(self, project_id: UUID) -> None:
        self.in_memory_project_repository.pop(project_id, None)
