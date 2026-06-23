from typing import Protocol
from uuid import UUID
from src.domain.entities.task_status_change import TaskStatusChange


class TaskStatusHistoryRepositoryPort(Protocol):
    async def append(self, change: TaskStatusChange) -> None:
        pass

    async def list_by_task_id(
        self, task_id: UUID, limit: int, offset: int
    ) -> list[TaskStatusChange]:
        pass
