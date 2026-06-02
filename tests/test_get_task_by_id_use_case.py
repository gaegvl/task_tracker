import pytest
from src.application.use_cases.create_project import (
    CreateProjectCommand,
    CreateProjectUseCase,
)
from src.infrastructure.db.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)
from src.application.use_cases.create_task import CreateTaskCommand, CreateTaskUseCase
from src.application.use_cases.get_task_by_id import (
    GetTaskByIdCommand,
    GetTaskByIdUseCase,
)
from src.domain.exceptions import TaskNotFoundError
from src.infrastructure.db.repositories.in_memory_task_repository import (
    InMemoryTaskRepository,
)
from uuid import uuid4


@pytest.mark.asyncio
async def test_get_task_by_id_use_case() -> None:
    repository = InMemoryTaskRepository()
    project_repository = InMemoryProjectRepository()
    create_project_use_case = CreateProjectUseCase(project_repository)
    command = CreateProjectCommand(name="Test Project", description="Test Description")
    result = await create_project_use_case.execute(command=command)
    create_use_case = CreateTaskUseCase(repository, project_repository)
    command = CreateTaskCommand(
        title="Test Task", description="Test Description", project_id=result.id
    )

    result = await create_use_case.execute(command=command)

    get_task_by_id_use_case = GetTaskByIdUseCase(repository)
    get_command = GetTaskByIdCommand(id=result.id)

    get_result = await get_task_by_id_use_case.execute(command=get_command)

    assert get_result.id == result.id


@pytest.mark.asyncio
async def test_get_task_by_id_use_case_not_found() -> None:
    repository = InMemoryTaskRepository()
    get_task_by_id_use_case = GetTaskByIdUseCase(repository)
    get_command = GetTaskByIdCommand(id=uuid4())

    with pytest.raises(TaskNotFoundError):
        await get_task_by_id_use_case.execute(command=get_command)
