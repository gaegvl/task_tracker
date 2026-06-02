from uuid import UUID
from src.domain.exceptions import TaskNotFoundError
from src.domain.entities.task import Task, TaskStatus
from src.application.ports.task_repository import TaskRepositoryPort
from operator import attrgetter


class InMemoryTaskRepository(TaskRepositoryPort):
    def __init__(self) -> None:
        self.in_memory_task_repository: dict[UUID, Task] = {}

    async def add(self, task: Task) -> None:
        self.in_memory_task_repository[task.id] = task

    async def get_by_id(self, task_id: UUID) -> Task:
        task = self.in_memory_task_repository.get(task_id)
        if not task:
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
        sorted_task_by_created_at = sorted(
            self.in_memory_task_repository.values(),
            key=attrgetter("created_at"),
            reverse=True,
        )
        if project_id:
            sorted_task_by_created_at = [
                task
                for task in sorted_task_by_created_at
                if task.project_id == project_id
            ]
        if status:
            sorted_task_by_created_at = [
                task for task in sorted_task_by_created_at if task.status == status
            ]
        return sorted_task_by_created_at[offset : offset + limit]

    async def delete(self, task_id: UUID) -> None:
        del self.in_memory_task_repository[task_id]

    async def exists_by_project_id(self, project_id: UUID) -> bool:
        return any(
            task.project_id == project_id
            for task in self.in_memory_task_repository.values()
        )
