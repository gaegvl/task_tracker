from uuid import UUID
from src.application.ports.task_repository import TaskRepositoryPort
from dataclasses import dataclass
from src.application.use_cases.get_task_by_id import GetTaskByIdResult


@dataclass(frozen=True)
class RestoreTaskCommand:
    task_id: UUID


class RestoreTaskUseCase:
    def __init__(self, task_repository: TaskRepositoryPort) -> None:
        self.task_repository = task_repository

    async def execute(self, command: RestoreTaskCommand) -> GetTaskByIdResult:
        task = await self.task_repository.restore(command.task_id)
        return GetTaskByIdResult.from_entity(task)
