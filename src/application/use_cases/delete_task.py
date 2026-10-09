from dataclasses import dataclass
from uuid import UUID

from src.application.ports.clock import ClockPort
from src.application.ports.task_repository import TaskRepositoryPort
from src.domain.exceptions import AuthorizationError


@dataclass(frozen=True)
class DeleteTaskCommand:
    task_id: UUID
    actor_id: UUID
    actor_is_admin: bool


class DeleteTaskUseCase:
    def __init__(self, task_repository: TaskRepositoryPort, clock: ClockPort) -> None:
        self.task_repository = task_repository
        self.clock = clock

    async def execute(self, command: DeleteTaskCommand) -> None:
        task = await self.task_repository.get_by_id(command.task_id)
        if not command.actor_is_admin:
            if task.created_by is None or task.created_by != command.actor_id:
                raise AuthorizationError(
                    f"User {command.actor_id} is not allowed to delete task {command.task_id}"  # noqa: E501
                )
        await self.task_repository.delete(command.task_id, self.clock.now())
