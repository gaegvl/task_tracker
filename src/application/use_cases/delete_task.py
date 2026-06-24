from dataclasses import dataclass
from uuid import UUID

from src.application.ports.clock import ClockPort
from src.application.ports.task_repository import TaskRepositoryPort


@dataclass(frozen=True)
class DeleteTaskCommand:
    task_id: UUID


class DeleteTaskUseCase:
    def __init__(self, task_repository: TaskRepositoryPort, clock: ClockPort) -> None:
        self.task_repository = task_repository
        self.clock = clock

    async def execute(self, command: DeleteTaskCommand) -> None:
        await self.task_repository.get_by_id(command.task_id)
        await self.task_repository.delete(command.task_id, self.clock.now())
