from uuid import UUID

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.entities.task import TaskStatus


class DomainError(Exception):
    pass


class InvalidTaskTitleError(DomainError):
    pass


class TaskNotFoundError(DomainError):
    def __init__(self, task_id: UUID) -> None:
        self.task_id = task_id
        super().__init__(f"Task with id {task_id} not found")


class InvalidProjectNameError(DomainError):
    pass


class ProjectNotFoundError(DomainError):
    def __init__(self, project_id: UUID) -> None:
        self.project_id = project_id
        super().__init__(f"Project with id {project_id} not found")


class ProjectHasTasksError(DomainError):
    def __init__(self, project_id: UUID) -> None:
        self.project_id = project_id
        super().__init__(f"Project with id {project_id} has tasks")


class InvalidTaskStatusTransitionError(DomainError):
    def __init__(self, old_status: TaskStatus, new_status: TaskStatus) -> None:
        self.old_status = old_status
        self.new_status = new_status
        super().__init__(
            f"Invalid task status transition from {old_status} to {new_status}"
        )
