import pytest

from src.application.use_cases.create_task import CreateTaskCommand, CreateTaskUseCase
from src.domain.entities.task import TaskStatus
from src.domain.exceptions import InvalidTaskTitleError, ProjectNotFoundError
from src.infrastructure.db.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)
from src.infrastructure.db.repositories.in_memory_task_repository import (
    InMemoryTaskRepository,
)
from tests.helpers import create_project_in_memory
from uuid import uuid4


@pytest.mark.asyncio
async def test_create_task_use_case_returns_created_task() -> None:
    project_repository = InMemoryProjectRepository()
    task_repository = InMemoryTaskRepository()
    project_id = await create_project_in_memory(project_repository)
    use_case = CreateTaskUseCase(
        task_repository=task_repository, project_repository=project_repository
    )

    result = await use_case.execute(
        command=CreateTaskCommand(
            title="Test Task", description="Test Description", project_id=project_id
        )
    )

    assert result.title == "Test Task"
    assert result.status == TaskStatus.TODO.value


@pytest.mark.asyncio
async def test_create_task_use_case_persists_task_in_repository() -> None:
    project_repository = InMemoryProjectRepository()
    task_repository = InMemoryTaskRepository()
    project_id = await create_project_in_memory(project_repository)
    use_case = CreateTaskUseCase(
        task_repository=task_repository, project_repository=project_repository
    )

    result = await use_case.execute(
        command=CreateTaskCommand(
            title="Test Task", description="Test Description", project_id=project_id
        )
    )

    saved = await task_repository.get_by_id(result.id)
    assert saved is not None


@pytest.mark.asyncio
async def test_create_task_use_case_invalid_title() -> None:
    project_repository = InMemoryProjectRepository()
    task_repository = InMemoryTaskRepository()
    use_case = CreateTaskUseCase(
        task_repository=task_repository, project_repository=project_repository
    )

    with pytest.raises(InvalidTaskTitleError):
        await use_case.execute(
            command=CreateTaskCommand(
                title="  a ", description=None, project_id=uuid4()
            )
        )


@pytest.mark.asyncio
async def test_create_task_use_case_project_not_found() -> None:
    project_repository = InMemoryProjectRepository()
    task_repository = InMemoryTaskRepository()
    use_case = CreateTaskUseCase(
        task_repository=task_repository, project_repository=project_repository
    )

    with pytest.raises(ProjectNotFoundError):
        await use_case.execute(
            command=CreateTaskCommand(
                title="Test Task",
                description="Test Description",
                project_id=uuid4(),
            )
        )
