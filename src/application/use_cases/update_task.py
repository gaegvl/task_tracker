from dataclasses import dataclass
from uuid import UUID

from src.application.ports.clock import ClockPort
from src.application.ports.id_generator import IdGeneratorPort
from src.application.ports.project_repository import ProjectRepositoryPort
from src.application.ports.task_repository import TaskRepositoryPort
from src.application.ports.task_status_history_repository import (
    TaskStatusHistoryRepositoryPort,
)
from src.application.use_cases.get_task_by_id import GetTaskByIdResult
from src.domain.entities.task import TaskStatus
from src.domain.entities.task_status_change import TaskStatusChange
from src.domain.exceptions import AuthorizationError


@dataclass
class UpdateTaskCommand:
    task_id: UUID
    status: TaskStatus
    actor_id: UUID
    actor_is_admin: bool
    title: str | None = None
    description: str | None = None
    project_id: UUID | None = None
    changed_by: UUID | None = None


class UpdateTaskUseCase:
    def __init__(
        self,
        task_repository: TaskRepositoryPort,
        project_repository: ProjectRepositoryPort,
        task_status_history_repository: TaskStatusHistoryRepositoryPort,
        clock: ClockPort,
        id_generator: IdGeneratorPort,
    ) -> None:
        self.task_repository = task_repository
        self.project_repository = project_repository
        self.task_status_history_repository = task_status_history_repository
        self.clock = clock
        self.id_generator = id_generator

    async def execute(self, command: UpdateTaskCommand) -> GetTaskByIdResult:
        task = await self.task_repository.get_by_id(command.task_id)
        if not command.actor_is_admin:
            if task.created_by is None or task.created_by != command.actor_id:
                raise AuthorizationError(
                    f"User {command.actor_id} is not allowed to modify task {command.task_id}"  # noqa: E501
                )
        old_status = task.status
        new_status = command.status
        if command.project_id:
            await self.project_repository.get_by_id(command.project_id)
        updated_task = task.apply_updates(
            status=command.status,
            title=command.title,
            description=command.description,
            project_id=command.project_id,
        )

        if old_status != new_status:
            change = TaskStatusChange(
                id=self.id_generator.new_id(),
                task_id=command.task_id,
                from_status=old_status,
                to_state=new_status,
                changed_at=self.clock.now(),
                changed_by=command.actor_id,
            )
            await self.task_status_history_repository.append(change)
        await self.task_repository.update(updated_task)
        return GetTaskByIdResult.from_entity(updated_task)
