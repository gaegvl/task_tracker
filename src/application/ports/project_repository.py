from typing import Protocol
from uuid import UUID
from src.domain.entities.project import Project


class ProjectRepositoryPort(Protocol):
    async def add(self, project: Project) -> None:
        pass

    async def get_by_id(self, project_id: UUID) -> Project:
        pass

    async def list_projects(self, limit, offsets) -> list[Project]:
        pass

    async def update(self, project: Project) -> None:
        pass

    async def delete(self, project_id: UUID) -> None:
        pass
