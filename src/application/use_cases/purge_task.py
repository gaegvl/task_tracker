from dataclasses import dataclass
from uuid import UUID

from src.application.ports.task_repository import TaskRepositoryPort


@dataclass(frozen=True)
class PurgeTaskCommand:
    task_id: UUID


class PurgeTaskUseCase:
    def __init__(self, task_repository: TaskRepositoryPort) -> None:
        self.task_repository = task_repository

    async def execute(self, command: PurgeTaskCommand) -> None:
        task = await self.task_repository.find_soft_deleted(command.task_id)
        await self.task_repository.purge(task)
