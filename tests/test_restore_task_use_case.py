import pytest
from uuid import uuid4
from src.domain.exceptions import TaskNotFoundError
from src.domain.entities.task import TaskStatus
from src.infrastructure.db.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)
from src.application.use_cases.restore_task import (
    RestoreTaskCommand,
    RestoreTaskUseCase,
)
from src.infrastructure.db.repositories.in_memory_task_repository import (
    InMemoryTaskRepository,
)
from tests.helpers import (
    create_project_in_memory,
    create_task_in_memory,
    add_tasks_to_repository,
)


@pytest.mark.asyncio
async def test_restore_task_use_case() -> None:
    task_repository = InMemoryTaskRepository()
    project_repository = InMemoryProjectRepository()
    project_id = await create_project_in_memory(project_repository)
    task_id = await create_task_in_memory(
        task_repository, project_repository, project_id
    )

    await task_repository.delete(task_id)

    use_case = RestoreTaskUseCase(task_repository=task_repository)
    command = RestoreTaskCommand(task_id=task_id)
    await use_case.execute(command=command)

    result = await task_repository.get_by_id(task_id)
    assert result.id == command.task_id
    assert result.title == "Test Task"
    assert result.description == "Test Description"
    assert result.project_id == project_id
    assert result.status == TaskStatus.TODO
    assert result.deleted_at is None


@pytest.mark.asyncio
async def test_restore_not_found_task() -> None:
    task_repository = InMemoryTaskRepository()
    use_case = RestoreTaskUseCase(task_repository=task_repository)
    command = RestoreTaskCommand(uuid4())
    with pytest.raises(TaskNotFoundError):
        await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_restore_before_deleted_task() -> None:
    task_repository = InMemoryTaskRepository()
    project_repository = InMemoryProjectRepository()
    project_id = await create_project_in_memory(project_repository)
    task_id = await create_task_in_memory(
        task_repository, project_repository, project_id
    )
    use_case = RestoreTaskUseCase(task_repository=task_repository)
    command = RestoreTaskCommand(task_id=task_id)
    with pytest.raises(TaskNotFoundError):
        await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_restore_task_after_delete_and_task_is_in_list_tasks() -> None:
    task_repository = InMemoryTaskRepository()
    project_repository = InMemoryProjectRepository()
    project_id = await create_project_in_memory(project_repository)
    task_id = await create_task_in_memory(
        task_repository, project_repository, project_id
    )
    await add_tasks_to_repository(3, project_id, TaskStatus.TODO, task_repository)

    await task_repository.delete(task_id)

    result = await task_repository.list_tasks(
        project_id=project_id, status=None, limit=10, offset=0
    )
    assert len(result) == 3
    assert task_id not in [task.id for task in result]
    use_case = RestoreTaskUseCase(task_repository=task_repository)
    command = RestoreTaskCommand(task_id=task_id)
    await use_case.execute(command=command)
    result = await task_repository.list_tasks(
        project_id=project_id, status=None, limit=10, offset=0
    )
    assert len(result) == 4
    assert task_id in [task.id for task in result]
