from dataclasses import dataclass, replace

from datetime import datetime
from uuid import UUID, uuid4


from src.domain.entities.task_status_change import TaskStatusChange
from src.application.use_cases.get_task_by_id import GetTaskByIdResult
from src.application.ports.task_repository import TaskRepositoryPort
from src.application.ports.project_repository import ProjectRepositoryPort
from src.domain.entities.task import TaskStatus
from src.application.ports.task_status_history_repository import (
    TaskStatusHistoryRepositoryPort,
)


@dataclass
class UpdateTaskCommand:
    task_id: UUID
    status: TaskStatus
    title: str | None = None
    description: str | None = None
    project_id: UUID | None = None


class UpdateTaskUseCase:
    def __init__(
        self,
        task_repository: TaskRepositoryPort,
        project_repository: ProjectRepositoryPort,
        task_status_history_repository: TaskStatusHistoryRepositoryPort,
    ) -> None:
        self.task_repository = task_repository
        self.project_repository = project_repository
        self.task_status_history_repository = task_status_history_repository

    async def execute(self, command: UpdateTaskCommand) -> GetTaskByIdResult:
        task = await self.task_repository.get_by_id(command.task_id)
        old_status = task.status
        new_status = command.status
        task.change_status(command.status)
        if old_status != new_status:
            change = TaskStatusChange(
                id=uuid4(),
                task_id=command.task_id,
                from_status=old_status,
                to_state=new_status,
                changed_at=datetime.now(),
            )
            await self.task_status_history_repository.append(change)
        if command.project_id:
            await self.project_repository.get_by_id(command.project_id)
        updated_task = replace(
            task,
            status=command.status,
            title=command.title or task.title,
            description=command.description or task.description,
            project_id=command.project_id or task.project_id,
        )
        await self.task_repository.update(updated_task)
        return GetTaskByIdResult.from_entity(updated_task)
