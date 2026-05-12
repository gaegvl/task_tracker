from uuid import uuid4
import pytest

from src.application.use_cases.create_task import CreateTaskCommand, CreateTaskUseCase
from src.infrastructure.db.repositories.in_memory_task_repository import (
    InMemoryTaskRepository,
)
from src.domain.entities.task import TaskStatus
from src.domain.exceptions import InvalidTaskTitleError


@pytest.mark.asyncio
async def test_create_task_use_case_success() -> None:
    repository = InMemoryTaskRepository()
    use_case = CreateTaskUseCase(task_repository=repository)

    command = CreateTaskCommand(
        title="Test Task", description="Test Description", project_id=uuid4()
    )

    result = await use_case.execute(command=command)

    assert result.title == "Test Task"
    assert result.status == TaskStatus.TODO.value
    saved = await repository.get_by_id(result.id)
    assert saved is not None


@pytest.mark.asyncio
async def test_create_task_use_case_invalid_title() -> None:
    repository = InMemoryTaskRepository()
    use_case = CreateTaskUseCase(task_repository=repository)

    command = CreateTaskCommand(title="  a ", description=None, project_id=uuid4())

    with pytest.raises(InvalidTaskTitleError):
        await use_case.execute(command=command)
