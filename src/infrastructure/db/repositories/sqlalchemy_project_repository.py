from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.exceptions import ProjectNotFoundError
from src.application.ports.project_repository import ProjectRepositoryPort
from src.domain.entities.project import Project
from src.infrastructure.db.models.project import Project as ProjectModel
from sqlalchemy import select, update
from uuid import UUID


class SqlAlchemyProjectRepository(ProjectRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, project: Project) -> None:
        project = ProjectModel(
            id=project.id,
            name=project.name,
            description=project.description,
            created_at=project.created_at,
            deleted_at=None,
        )
        self.session.add(project)
        await self.session.commit()

    async def get_by_id(self, project_id: UUID) -> Project:
        project = await self.session.scalar(
            select(ProjectModel).where(
                ProjectModel.id == project_id, ProjectModel.deleted_at.is_(None)
            )
        )
        if not project:
            raise ProjectNotFoundError(project_id)
        return Project(
            id=project.id,
            name=project.name,
            description=project.description,
            created_at=project.created_at,
        )

    async def update(self, project: Project) -> None:
        await self.session.execute(
            update(ProjectModel)
            .where(ProjectModel.id == project.id, ProjectModel.deleted_at.is_(None))
            .values(name=project.name, description=project.description)
        )
        await self.session.commit()

    async def list_projects(self, limit, offsets) -> list[Project]:
        projects = await self.session.scalars(
            select(ProjectModel)
            .where(ProjectModel.deleted_at.is_(None))
            .offset(offsets)
            .limit(limit)
        )
        return [
            Project(
                id=project.id,
                name=project.name,
                description=project.description,
                created_at=project.created_at,
            )
            for project in projects
        ]

    async def delete(self, project_id: UUID) -> None:
        project = await self.get_by_id(project_id)
        marked = project.mark_deleted(datetime.now())
        await self.session.execute(
            update(ProjectModel)
            .where(ProjectModel.id == project_id, ProjectModel.deleted_at.is_(None))
            .values(deleted_at=marked.deleted_at)
        )
        await self.session.commit()
