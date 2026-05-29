from dataclasses import dataclass
from src.application.ports.task_repository import TaskRepositoryPort

from uuid import UUID


@dataclass(frozen=True)
class DeleteTaskCommand:
    task_id: UUID


class DeleteTaskUseCase:
    def __init__(self, task_repository: TaskRepositoryPort) -> None:
        self.task_repository = task_repository

    async def execute(self, command: DeleteTaskCommand) -> None:
        await self.task_repository.get_by_id(command.task_id)
        await self.task_repository.delete(command.task_id)
