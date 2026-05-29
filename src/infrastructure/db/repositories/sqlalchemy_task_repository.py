from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.ports.task_repository import TaskRepositoryPort
from src.domain.entities.task import Task, TaskStatus
from src.infrastructure.db.models.task import Task as TaskModel
from sqlalchemy import delete, select, update


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
        )
        self.session.add(task_model)
        await self.session.commit()

    async def get_by_id(self, task_id: UUID) -> Task | None:
        task = await self.session.scalar(
            select(TaskModel).where(TaskModel.id == task_id)
        )
        if not task:
            raise TaskNotFoundError(task_id)
        return Task(
            id=task.id,
            title=task.title,
            description=task.description,
            project_id=task.project_id,
            status=task.status,
            created_at=task.created_at,
        )

    async def update(self, task: Task) -> None:
        get_task = await self.get_by_id(task.id)
        updated_task = await self.session.execute(
            update(TaskModel)
            .where(TaskModel.id == get_task.id)
            .values(
                title=task.title,
                description=task.description,
                project_id=task.project_id,
                status=task.status.value,
            )
        )
        if not updated_task:
            raise TaskNotFoundError(task.id)
        await self.session.commit()

    async def list_tasks(
        self,
        project_id: UUID | None,
        status: TaskStatus | None,
        limit: int,
        offset: int,
    ) -> list[Task]:
        filters = []
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
                status=task.status,
                created_at=task.created_at,
            )
            for task in tasks
        ]

    async def delete(self, task_id: UUID) -> None:
        await self.session.execute(delete(TaskModel).where(TaskModel.id == task_id))
        await self.session.commit()
