from typing import Protocol
from uuid import UUID
from src.domain.entities.task import Task, TaskStatus


class TaskRepositoryPort(Protocol):
    async def add(self, task: Task) -> None:
        pass

    async def get_by_id(self, task_id: UUID) -> Task:
        pass

    async def update(self, task: Task) -> None:
        pass

    async def list_tasks(
        self,
        project_id: UUID | None,
        status: TaskStatus | None,
        limit: int,
        offset: int,
    ) -> list[Task]:
        pass

    async def delete(self, task_id: UUID) -> None:
        pass

    async def exists_by_project_id(self, project_id: UUID) -> bool:
        pass
