import pytest
from uuid import uuid4

from src.application.use_cases.create_task import CreateTaskCommand, CreateTaskUseCase
from src.application.use_cases.delete_task import DeleteTaskCommand, DeleteTaskUseCase
from src.domain.exceptions import TaskNotFoundError
from src.infrastructure.db.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)
from src.infrastructure.db.repositories.in_memory_task_repository import (
    InMemoryTaskRepository,
)
from tests.helpers import create_project_in_memory, create_task_in_memory


@pytest.mark.asyncio
async def test_delete_task_use_case_removes_task_from_repository() -> None:
    project_repository = InMemoryProjectRepository()
    project_id = await create_project_in_memory(project_repository)
    task_repository = InMemoryTaskRepository()
    task_id = await create_task_in_memory(
        task_repository, project_repository, project_id
    )

    delete_use_case = DeleteTaskUseCase(task_repository)
    await delete_use_case.execute(command=DeleteTaskCommand(task_id=task_id))

    with pytest.raises(TaskNotFoundError):
        await task_repository.get_by_id(task_id)


@pytest.mark.asyncio
async def test_delete_task_use_case_not_found() -> None:
    repository = InMemoryTaskRepository()
    delete_task = DeleteTaskUseCase(repository)

    with pytest.raises(TaskNotFoundError):
        await delete_task.execute(command=DeleteTaskCommand(task_id=uuid4()))


@pytest.mark.asyncio
async def test_delete_task_use_case_soft_deleted_not_found_on_get() -> None:
    project_repository = InMemoryProjectRepository()
    project_id = await create_project_in_memory(project_repository)
    task_repository = InMemoryTaskRepository()
    task_id = await create_task_in_memory(
        task_repository, project_repository, project_id
    )
    delete_use_case = DeleteTaskUseCase(task_repository)
    await delete_use_case.execute(command=DeleteTaskCommand(task_id=task_id))

    with pytest.raises(TaskNotFoundError):
        await task_repository.get_by_id(task_id)


@pytest.mark.asyncio
async def test_delete_task_use_case_soft_deleted_raises_on_second_delete() -> None:
    project_repository = InMemoryProjectRepository()
    project_id = await create_project_in_memory(project_repository)
    task_repository = InMemoryTaskRepository()
    task_id = await create_task_in_memory(
        task_repository, project_repository, project_id
    )
    delete_use_case = DeleteTaskUseCase(task_repository)
    delete_command = DeleteTaskCommand(task_id=task_id)
    await delete_use_case.execute(command=delete_command)

    with pytest.raises(TaskNotFoundError):
        await delete_use_case.execute(command=delete_command)


@pytest.mark.asyncio
async def test_delete_task_use_case_soft_deleted_excluded_from_list() -> None:
    project_repository = InMemoryProjectRepository()
    project_id = await create_project_in_memory(project_repository)
    task_repository = InMemoryTaskRepository()
    create_use_case = CreateTaskUseCase(task_repository, project_repository)
    task_result_1 = await create_use_case.execute(
        command=CreateTaskCommand(
            title="Test Task", description="Test Description", project_id=project_id
        )
    )
    await create_use_case.execute(
        command=CreateTaskCommand(
            title="Test Task 2",
            description="Test Description 2",
            project_id=project_id,
        )
    )
    await create_use_case.execute(
        command=CreateTaskCommand(
            title="Test Task 3",
            description="Test Description 3",
            project_id=project_id,
        )
    )
    delete_use_case = DeleteTaskUseCase(task_repository)
    await delete_use_case.execute(command=DeleteTaskCommand(task_id=task_result_1.id))

    tasks = await task_repository.list_tasks(
        project_id=project_id, status=None, limit=10, offset=0
    )

    assert len(tasks) == 2
