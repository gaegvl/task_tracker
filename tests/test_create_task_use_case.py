from uuid import uuid4
import pytest

from src.application.use_cases.create_project import (
    CreateProjectCommand,
    CreateProjectUseCase,
)
from src.infrastructure.db.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)
from src.application.use_cases.create_task import CreateTaskCommand, CreateTaskUseCase
from src.infrastructure.db.repositories.in_memory_task_repository import (
    InMemoryTaskRepository,
)
from src.domain.entities.task import TaskStatus
from src.domain.exceptions import InvalidTaskTitleError, ProjectNotFoundError


@pytest.mark.asyncio
async def test_create_task_use_case_success() -> None:
    repository = InMemoryTaskRepository()
    project_repository = InMemoryProjectRepository()
    create_project_use_case = CreateProjectUseCase(
        project_repository=project_repository
    )
    command = CreateProjectCommand(name="Test Project", description="Test Description")
    result = await create_project_use_case.execute(command=command)

    use_case = CreateTaskUseCase(
        task_repository=repository, project_repository=project_repository
    )

    command = CreateTaskCommand(
        title="Test Task", description="Test Description", project_id=result.id
    )

    result = await use_case.execute(command=command)

    assert result.title == "Test Task"
    assert result.status == TaskStatus.TODO.value
    saved = await repository.get_by_id(result.id)
    assert saved is not None


@pytest.mark.asyncio
async def test_create_task_use_case_invalid_title() -> None:
    repository = InMemoryTaskRepository()
    project_repository = InMemoryProjectRepository()
    use_case = CreateTaskUseCase(
        task_repository=repository, project_repository=project_repository
    )

    command = CreateTaskCommand(title="  a ", description=None, project_id=uuid4())

    with pytest.raises(InvalidTaskTitleError):
        await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_create_task_use_case_project_not_found() -> None:
    repository = InMemoryTaskRepository()
    project_repository = InMemoryProjectRepository()
    use_case = CreateTaskUseCase(
        task_repository=repository, project_repository=project_repository
    )

    command = CreateTaskCommand(
        title="Test Task", description="Test Description", project_id=uuid4()
    )

    with pytest.raises(ProjectNotFoundError):
        await use_case.execute(command=command)
