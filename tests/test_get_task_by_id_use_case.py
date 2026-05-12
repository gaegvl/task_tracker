import pytest
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
    create_use_case = CreateTaskUseCase(repository)
    command = CreateTaskCommand(
        title="Test Task", description="Test Description", project_id=uuid4()
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
