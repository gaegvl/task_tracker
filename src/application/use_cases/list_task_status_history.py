from dataclasses import dataclass
from uuid import UUID

from src.application.ports.task_repository import TaskRepositoryPort
from src.application.ports.task_status_history_repository import (
    TaskStatusHistoryRepositoryPort,
)
from src.domain.entities.task_status_change import TaskStatusChange


@dataclass(frozen=True)
class ListTaskStatusHistoryCommand:
    task_id: UUID
    limit: int
    offset: int


class ListTaskStatusHistoryUseCase:
    def __init__(
        self,
        task_status_history_repository: TaskStatusHistoryRepositoryPort,
        task_repository: TaskRepositoryPort,
    ) -> None:
        self.task_status_history_repository = task_status_history_repository
        self.task_repository = task_repository

    async def execute(
        self, command: ListTaskStatusHistoryCommand
    ) -> list[TaskStatusChange]:
        await self.task_repository.get_by_id(command.task_id)
        changes = await self.task_status_history_repository.list_by_task_id(
            command.task_id, command.limit, command.offset
        )
        return changes
