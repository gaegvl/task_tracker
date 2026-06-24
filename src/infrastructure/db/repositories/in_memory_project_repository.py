from datetime import datetime
from uuid import UUID

from src.application.ports.project_repository import ProjectRepositoryPort
from src.domain.entities.project import Project
from src.domain.exceptions import ProjectNotFoundError


class InMemoryProjectRepository(ProjectRepositoryPort):
    def __init__(self) -> None:
        self.in_memory_project_repository: dict[UUID, Project] = {}

    async def add(self, project: Project) -> None:
        self.in_memory_project_repository[project.id] = project

    async def get_by_id(self, project_id: UUID) -> Project:
        project = self.in_memory_project_repository.get(project_id)
        if not project or project.deleted_at is not None:
            raise ProjectNotFoundError(project_id)
        return project

    async def update(self, project: Project) -> None:
        await self.get_by_id(project.id)
        self.in_memory_project_repository[project.id] = project

    async def list_projects(self, limit: int, offset: int) -> list[Project]:
        return list(
            project
            for project in self.in_memory_project_repository.values()
            if project.deleted_at is None
        )[offset : offset + limit]

    async def delete(self, project_id: UUID, deleted_at: datetime) -> None:
        project = await self.get_by_id(project_id)
        self.in_memory_project_repository[project_id] = project.mark_deleted(deleted_at)

    async def find_soft_deleted(self, project_id: UUID) -> Project:
        project = self.in_memory_project_repository.get(project_id)
        if not project or project.deleted_at is None:
            raise ProjectNotFoundError(project_id)
        return project

    async def restore(self, project_id: UUID) -> Project:
        project = self.in_memory_project_repository.get(project_id)
        if not project or project.deleted_at is None:
            raise ProjectNotFoundError(project_id)
        restored_project = project.restore()
        self.in_memory_project_repository[project_id] = restored_project
        return restored_project

    async def purge(self, project: Project) -> None:
        self.in_memory_project_repository.pop(project.id)
