from dataclasses import dataclass
from uuid import UUID

from src.application.ports.task_repository import TaskRepositoryPort
from src.application.use_cases.get_task_by_id import GetTaskByIdResult
from src.domain.entities.task import TaskStatus


@dataclass
class ListTasksCommand:
    project_id: UUID | None
    status: TaskStatus | None
    limit: int
    offset: int


@dataclass
class ListTaskResult:
    items: list[GetTaskByIdResult]


class ListTaskUseCase:
    def __init__(self, task_repository: TaskRepositoryPort) -> None:
        self.task_repository = task_repository

    async def execute(self, command: ListTasksCommand) -> ListTaskResult:
        tasks = await self.task_repository.list_tasks(
            project_id=command.project_id,
            status=command.status,
            limit=command.limit,
            offset=command.offset,
        )
        return ListTaskResult(
            items=[GetTaskByIdResult.from_entity(task) for task in tasks]
        )
