from uuid import UUID
from src.domain.exceptions import TaskNotFoundError
from src.domain.entities.task import Task, TaskStatus
from src.application.ports.task_repository import TaskRepositoryPort
from operator import attrgetter
from datetime import datetime


class InMemoryTaskRepository(TaskRepositoryPort):
    def __init__(self) -> None:
        self.in_memory_task_repository: dict[UUID, Task] = {}

    async def add(self, task: Task) -> None:
        self.in_memory_task_repository[task.id] = task

    async def get_by_id(self, task_id: UUID) -> Task:
        task = self.in_memory_task_repository.get(task_id)
        if not task:
            raise TaskNotFoundError(task_id)
        if task.deleted_at is not None:
            raise TaskNotFoundError(task_id)
        return task

    async def update(self, task: Task) -> None:
        self.in_memory_task_repository[task.id] = task

    async def list_tasks(
        self,
        project_id: UUID | None,
        status: TaskStatus | None,
        limit: int,
        offset: int,
    ) -> list[Task]:
        filtered_tasks = [
            task
            for task in self.in_memory_task_repository.values()
            if task.deleted_at is None
        ]
        if project_id:
            filtered_tasks = [
                task for task in filtered_tasks if task.project_id == project_id
            ]
        if status:
            filtered_tasks = [task for task in filtered_tasks if task.status == status]

        sorted_task_by_created_at = sorted(
            filtered_tasks,
            key=attrgetter("created_at"),
            reverse=True,
        )
        return sorted_task_by_created_at[offset : offset + limit]

    async def delete(self, task_id: UUID) -> None:
        task = await self.get_by_id(task_id)
        self.in_memory_task_repository[task_id] = task.mark_deleted(datetime.now())

    async def exists_by_project_id(self, project_id: UUID) -> bool:
        return any(
            task.project_id == project_id and task.deleted_at is None
            for task in self.in_memory_task_repository.values()
        )
