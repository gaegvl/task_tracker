from typing import Protocol
from uuid import UUID
from src.domain.entities.task import Task


class TaskRepositoryPort(Protocol):
    async def add(self, task: Task) -> None:
        pass

    async def get_by_id(self, task_id: UUID) -> Task | None:
        pass
