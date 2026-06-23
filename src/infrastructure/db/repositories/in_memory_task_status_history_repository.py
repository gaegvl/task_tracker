import operator
from src.application.ports.task_status_history_repository import (
    TaskStatusHistoryRepositoryPort,
)
from uuid import UUID
from src.domain.entities.task_status_change import TaskStatusChange


class InMemoryTaskStatusHistoryRepository(TaskStatusHistoryRepositoryPort):
    def __init__(self) -> None:
        self.in_memory_task_status_history_repository: dict[UUID, TaskStatusChange] = {}

    async def append(self, change: TaskStatusChange) -> None:
        self.in_memory_task_status_history_repository[change.id] = change

    async def list_by_task_id(
        self, task_id: UUID, limit: int, offset: int
    ) -> list[TaskStatusChange]:
        return list(
            sorted(
                [
                    task
                    for task in self.in_memory_task_status_history_repository.values()
                    if task.task_id == task_id
                ],
                key=operator.attrgetter("changed_at"),
            ),
        )[offset : offset + limit]
