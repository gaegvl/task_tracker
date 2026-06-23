from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.entities.task_status_change import TaskStatusChange
from src.domain.entities.task import TaskStatus
from src.infrastructure.db.models import TaskStatusChange as TaskStatusChangeModel
from src.application.ports.task_status_history_repository import (
    TaskStatusHistoryRepositoryPort,
)


class SqlAlchemyTaskStatusHistoryRepository(TaskStatusHistoryRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def append(self, change: TaskStatusChange) -> None:
        task_status_change_model = TaskStatusChangeModel(
            id=change.id,
            task_id=change.task_id,
            from_status=change.from_status.value,
            to_state=change.to_state.value,
            changed_at=change.changed_at,
        )
        self.session.add(task_status_change_model)
        await self.session.commit()

    async def list_by_task_id(
        self, task_id: UUID, limit: int, offset: int
    ) -> list[TaskStatusChange]:
        result = await self.session.scalars(
            select(TaskStatusChangeModel)
            .where(TaskStatusChangeModel.task_id == task_id)
            .order_by(TaskStatusChangeModel.changed_at.asc())
            .offset(offset)
            .limit(limit)
        )
        result = result.all()
        return [
            TaskStatusChange(
                id=change.id,
                task_id=change.task_id,
                from_status=TaskStatus(change.from_status),
                to_state=TaskStatus(change.to_state),
                changed_at=change.changed_at,
            )
            for change in result
        ]
