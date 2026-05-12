from uuid import UUID


class DomainError(Exception):
    pass


class InvalidTaskTitleError(DomainError):
    pass


class TaskNotFoundError(DomainError):
    def __init__(self, task_id: UUID) -> None:
        self.task_id = task_id
        super().__init__(f"Task with id {task_id} not found")
