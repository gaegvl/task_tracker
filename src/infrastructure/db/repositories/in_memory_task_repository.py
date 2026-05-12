from uuid import UUID
from src.domain.entities.task import Task
from src.application.ports.task_repository import TaskRepositoryPort


class InMemoryTaskRepository(TaskRepositoryPort):
    def __init__(self) -> None:
        self.in_memory_task_repository: dict[UUID, Task] = {}

    async def add(self, task: Task) -> None:
        self.in_memory_task_repository[task.id] = task

    async def get_by_id(self, task_id: UUID) -> Task | None:
        return self.in_memory_task_repository.get(task_id)
