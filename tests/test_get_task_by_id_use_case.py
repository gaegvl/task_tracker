import pytest

from src.application.use_cases.create_project import CreateProjectCommand
from src.application.use_cases.create_task import CreateTaskCommand
from src.application.use_cases.get_task_by_id import (
    GetTaskByIdCommand,
    GetTaskByIdUseCase,
)
from src.domain.exceptions import TaskNotFoundError
from src.infrastructure.db.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)
from src.infrastructure.db.repositories.in_memory_task_repository import (
    InMemoryTaskRepository,
)
from tests.helpers import (
    TEST_ID_GENERATOR,
    make_create_project_use_case,
    make_create_task_use_case,
)


@pytest.mark.asyncio
async def test_get_task_by_id_use_case() -> None:
    repository = InMemoryTaskRepository()
    project_repository = InMemoryProjectRepository()
    create_project_use_case = make_create_project_use_case(
        project_repository=project_repository
    )
    command = CreateProjectCommand(name="Test Project", description="Test Description")
    result = await create_project_use_case.execute(command=command)
    create_use_case = make_create_task_use_case(
        task_repository=repository,
        project_repository=project_repository,
    )
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
    get_command = GetTaskByIdCommand(id=TEST_ID_GENERATOR.new_id())

    with pytest.raises(TaskNotFoundError):
        await get_task_by_id_use_case.execute(command=get_command)
