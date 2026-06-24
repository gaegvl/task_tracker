from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.exceptions import TaskNotFoundError
from src.application.ports.task_repository import TaskRepositoryPort
from src.domain.entities.task import Task, TaskStatus
from src.infrastructure.db.models.task import Task as TaskModel
from sqlalchemy import delete, update, exists, select
from datetime import datetime


class SqlAlchemyTaskRepository(TaskRepositoryPort):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, task: Task) -> None:
        task_model = TaskModel(
            id=task.id,
            title=task.title,
            description=task.description,
            project_id=task.project_id,
            status=task.status.value,
            created_at=task.created_at,
            deleted_at=None,
        )
        self.session.add(task_model)
        await self.session.commit()

    async def get_by_id(self, task_id: UUID) -> Task:
        task = await self.session.scalar(
            select(TaskModel).where(
                TaskModel.id == task_id, TaskModel.deleted_at.is_(None)
            )
        )
        if not task:
            raise TaskNotFoundError(task_id)
        return Task(
            id=task.id,
            title=task.title,
            description=task.description,
            project_id=task.project_id,
            status=TaskStatus(task.status),
            created_at=task.created_at,
        )

    async def update(self, task: Task) -> None:
        await self.session.execute(
            update(TaskModel)
            .where(TaskModel.id == task.id, TaskModel.deleted_at.is_(None))
            .values(
                title=task.title,
                description=task.description,
                project_id=task.project_id,
                status=task.status.value,
            )
        )
        await self.session.commit()

    async def list_tasks(
        self,
        project_id: UUID | None,
        status: TaskStatus | None,
        limit: int,
        offset: int,
    ) -> list[Task]:
        filters = [TaskModel.deleted_at.is_(None)]
        if project_id:
            filters.append(TaskModel.project_id == project_id)
        if status:
            filters.append(TaskModel.status == status.value)
        tasks = await self.session.scalars(
            select(TaskModel)
            .where(*filters)
            .order_by(TaskModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return [
            Task(
                id=task.id,
                title=task.title,
                description=task.description,
                project_id=task.project_id,
                status=TaskStatus(task.status),
                created_at=task.created_at,
            )
            for task in tasks
        ]

    async def delete(self, task_id: UUID) -> None:
        task = await self.get_by_id(task_id)
        marked = task.mark_deleted(datetime.now())
        await self.session.execute(
            update(TaskModel)
            .where(TaskModel.id == task_id, TaskModel.deleted_at.is_(None))
            .values(deleted_at=marked.deleted_at)
        )
        await self.session.commit()

    async def exists_by_project_id(self, project_id: UUID) -> bool:
        exists_query = exists(TaskModel).where(
            TaskModel.project_id == project_id, TaskModel.deleted_at.is_(None)
        )
        result = await self.session.scalar(select(TaskModel).where(exists_query))
        return bool(result)

    async def find_soft_deleted(self, task_id: UUID) -> Task:
        task = await self.session.scalar(
            select(TaskModel).where(
                TaskModel.id == task_id, TaskModel.deleted_at.isnot(None)
            )
        )
        if not task:
            raise TaskNotFoundError(task_id)
        return Task(
            id=task.id,
            title=task.title,
            description=task.description,
            project_id=task.project_id,
            status=TaskStatus(task.status),
            created_at=task.created_at,
        )

    async def restore(self, task: Task) -> Task:
        await self.session.execute(
            update(TaskModel).where(TaskModel.id == task.id).values(deleted_at=None)
        )
        await self.session.commit()
        return Task(
            id=task.id,
            title=task.title,
            description=task.description,
            project_id=task.project_id,
            status=TaskStatus(task.status),
            created_at=task.created_at,
        )

    async def restore_by_project_id(self, project_id: UUID) -> None:
        await self.session.execute(
            update(TaskModel)
            .where(TaskModel.project_id == project_id, TaskModel.deleted_at.isnot(None))
            .values(deleted_at=None)
        )
        await self.session.commit()

    async def purge(self, task: Task) -> None:
        await self.session.execute(
            delete(TaskModel).where(
                TaskModel.id == task.id, TaskModel.deleted_at.isnot(None)
            )
        )
        await self.session.commit()

    async def purge_by_project_id(self, project_id: UUID) -> None:
        await self.session.execute(
            delete(TaskModel).where(
                TaskModel.project_id == project_id, TaskModel.deleted_at.isnot(None)
            )
        )
        await self.session.commit()
