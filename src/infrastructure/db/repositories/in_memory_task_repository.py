from uuid import UUID
from src.domain.entities.task import Task, TaskStatus
from src.domain.exceptions import TaskNotFoundError
from src.application.ports.task_repository import TaskRepositoryPort
from operator import attrgetter


class InMemoryTaskRepository(TaskRepositoryPort):
    def __init__(self) -> None:
        self.in_memory_task_repository: dict[UUID, Task] = {}

    async def add(self, task: Task) -> None:
        self.in_memory_task_repository[task.id] = task

    async def get_by_id(self, task_id: UUID) -> Task | None:
        return self.in_memory_task_repository.get(task_id)

    async def update(self, task: Task) -> None:
        if task.id not in self.in_memory_task_repository:
            raise TaskNotFoundError(task.id)
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
