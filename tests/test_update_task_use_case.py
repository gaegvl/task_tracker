import pytest
from uuid import uuid4
from src.application.use_cases.update_task import UpdateTaskCommand, UpdateTaskUseCase
from src.infrastructure.db.repositories.in_memory_task_repository import (
    InMemoryTaskRepository,
)
from src.domain.exceptions import TaskNotFoundError
from src.application.use_cases.create_task import CreateTaskCommand, CreateTaskUseCase
from src.domain.entities.task import TaskStatus


@pytest.mark.asyncio
async def test_update_task_use_case_success() -> None:
    repository = InMemoryTaskRepository()
    create_use_case = CreateTaskUseCase(repository)
    projec_id = uuid4()
    command = CreateTaskCommand(
        title="Test Task", description="Test Description", project_id=projec_id
    )
    task = await create_use_case.execute(command=command)

    update_use_case = UpdateTaskUseCase(repository)
    update_command = UpdateTaskCommand(task_id=task.id, status=TaskStatus.IN_PROGRESS)
    updated_task = await update_use_case.execute(command=update_command)
    assert updated_task.status == TaskStatus.IN_PROGRESS

    saved = await repository.get_by_id(updated_task.id)

    assert saved.status == TaskStatus.IN_PROGRESS
    assert saved.title == task.title
    assert saved.id == task.id
    assert saved.project_id == projec_id
    assert saved.description == "Test Description"

    update_command = UpdateTaskCommand(task_id=task.id, status=TaskStatus.DONE)
    updated_task = await update_use_case.execute(command=update_command)
    assert updated_task.status == TaskStatus.DONE


@pytest.mark.asyncio
async def test_update_task_use_case_not_found() -> None:
    repository = InMemoryTaskRepository()
    update_use_case = UpdateTaskUseCase(repository)
    update_command = UpdateTaskCommand(task_id=uuid4(), status=TaskStatus.IN_PROGRESS)

    with pytest.raises(TaskNotFoundError):
        await update_use_case.execute(command=update_command)
