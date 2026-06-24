import pytest

from src.application.use_cases.delete_task import DeleteTaskCommand
from src.application.use_cases.list_task_status_history import (
    ListTaskStatusHistoryCommand,
    ListTaskStatusHistoryUseCase,
)
from src.application.use_cases.update_task import UpdateTaskCommand
from src.domain.entities.task import TaskStatus
from src.domain.exceptions import InvalidTaskStatusTransitionError, TaskNotFoundError
from src.infrastructure.db.repositories import (
    in_memory_task_status_history_repository,
)
from src.infrastructure.db.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)
from src.infrastructure.db.repositories.in_memory_task_repository import (
    InMemoryTaskRepository,
)
from tests.helpers import (
    TEST_ID_GENERATOR,
    create_project_in_memory,
    create_task_in_memory,
    make_delete_task_use_case,
    make_update_task_use_case,
)

InMemoryTaskStatusHistoryRepository = (
    in_memory_task_status_history_repository.InMemoryTaskStatusHistoryRepository
)


@pytest.mark.asyncio
async def test_task_status_history_use_case() -> None:
    task_status_history_repository = InMemoryTaskStatusHistoryRepository()
    project_repository = InMemoryProjectRepository()
    project_id = await create_project_in_memory(project_repository)
    task_repository = InMemoryTaskRepository()
    task_id = await create_task_in_memory(
        task_repository, project_repository, project_id
    )
    history_use_case = ListTaskStatusHistoryUseCase(
        task_status_history_repository=task_status_history_repository,
        task_repository=task_repository,
    )
    history_command = ListTaskStatusHistoryCommand(task_id=task_id, limit=10, offset=0)
    result = await history_use_case.execute(command=history_command)
    assert result == []

    update_command = UpdateTaskCommand(task_id=task_id, status=TaskStatus.IN_PROGRESS)
    update_use_case = make_update_task_use_case(
        task_repository=task_repository,
        task_status_history_repository=task_status_history_repository,
        project_repository=project_repository,
    )
    await update_use_case.execute(command=update_command)

    result = await history_use_case.execute(command=history_command)
    assert len(result) == 1


@pytest.mark.asyncio
async def test_task_status_history_status_change_to_the_same_status() -> None:
    task_status_history_repository = InMemoryTaskStatusHistoryRepository()
    task_repository = InMemoryTaskRepository()
    project_repository = InMemoryProjectRepository()
    project_id = await create_project_in_memory(project_repository)
    task_id = await create_task_in_memory(
        task_repository, project_repository, project_id
    )
    history_use_case = ListTaskStatusHistoryUseCase(
        task_status_history_repository=task_status_history_repository,
        task_repository=task_repository,
    )
    history_command = ListTaskStatusHistoryCommand(task_id=task_id, limit=10, offset=0)

    update_command = UpdateTaskCommand(
        task_id=task_id, status=TaskStatus.TODO, title="Test Task 2"
    )
    update_use_case = make_update_task_use_case(
        task_repository=task_repository,
        task_status_history_repository=task_status_history_repository,
        project_repository=project_repository,
    )
    await update_use_case.execute(command=update_command)

    result = await history_use_case.execute(command=history_command)
    assert result == []


@pytest.mark.asyncio
async def test_task_status_history_invalid_status_transition() -> None:
    task_status_history_repository = InMemoryTaskStatusHistoryRepository()
    task_repository = InMemoryTaskRepository()
    project_repository = InMemoryProjectRepository()
    project_id = await create_project_in_memory(project_repository)
    task_id = await create_task_in_memory(
        task_repository, project_repository, project_id
    )
    history_use_case = ListTaskStatusHistoryUseCase(
        task_status_history_repository=task_status_history_repository,
        task_repository=task_repository,
    )
    history_command = ListTaskStatusHistoryCommand(task_id=task_id, limit=10, offset=0)

    update_command = UpdateTaskCommand(task_id=task_id, status=TaskStatus.DONE)
    update_use_case = make_update_task_use_case(
        task_repository=task_repository,
        task_status_history_repository=task_status_history_repository,
        project_repository=project_repository,
    )
    with pytest.raises(InvalidTaskStatusTransitionError):
        await update_use_case.execute(command=update_command)

    result = await history_use_case.execute(command=history_command)
    assert result == []


@pytest.mark.asyncio
async def test_task_status_history_two_status_changes() -> None:
    task_status_history_repository = InMemoryTaskStatusHistoryRepository()
    task_repository = InMemoryTaskRepository()
    project_repository = InMemoryProjectRepository()
    project_id = await create_project_in_memory(project_repository)
    task_id = await create_task_in_memory(
        task_repository, project_repository, project_id
    )
    history_use_case = ListTaskStatusHistoryUseCase(
        task_status_history_repository=task_status_history_repository,
        task_repository=task_repository,
    )
    history_command = ListTaskStatusHistoryCommand(task_id=task_id, limit=10, offset=0)

    update_command = UpdateTaskCommand(task_id=task_id, status=TaskStatus.IN_PROGRESS)
    update_use_case = make_update_task_use_case(
        task_repository=task_repository,
        task_status_history_repository=task_status_history_repository,
        project_repository=project_repository,
    )
    await update_use_case.execute(command=update_command)

    result = await history_use_case.execute(command=history_command)
    assert len(result) == 1

    update_command = UpdateTaskCommand(task_id=task_id, status=TaskStatus.DONE)
    update_use_case = make_update_task_use_case(
        task_repository=task_repository,
        task_status_history_repository=task_status_history_repository,
        project_repository=project_repository,
    )
    await update_use_case.execute(command=update_command)

    result = await history_use_case.execute(command=history_command)
    assert len(result) == 2


@pytest.mark.asyncio
async def test_task_status_history_two_status_changes_with_pagination() -> None:
    task_status_history_repository = InMemoryTaskStatusHistoryRepository()
    task_repository = InMemoryTaskRepository()
    project_repository = InMemoryProjectRepository()
    project_id = await create_project_in_memory(project_repository)
    task_id = await create_task_in_memory(
        task_repository, project_repository, project_id
    )
    history_use_case = ListTaskStatusHistoryUseCase(
        task_status_history_repository=task_status_history_repository,
        task_repository=task_repository,
    )
    history_command = ListTaskStatusHistoryCommand(task_id=task_id, limit=1, offset=0)
    update_command = UpdateTaskCommand(task_id=task_id, status=TaskStatus.IN_PROGRESS)
    update_use_case = make_update_task_use_case(
        task_repository=task_repository,
        task_status_history_repository=task_status_history_repository,
        project_repository=project_repository,
    )
    await update_use_case.execute(command=update_command)

    result = await history_use_case.execute(command=history_command)
    assert len(result) == 1

    history_command = ListTaskStatusHistoryCommand(task_id=task_id, limit=1, offset=1)
    result = await history_use_case.execute(command=history_command)
    assert result == []


@pytest.mark.asyncio
async def test_task_status_history_soft_delete() -> None:
    task_status_history_repository = InMemoryTaskStatusHistoryRepository()
    task_repository = InMemoryTaskRepository()
    project_repository = InMemoryProjectRepository()
    project_id = await create_project_in_memory(project_repository)
    task_id = await create_task_in_memory(
        task_repository, project_repository, project_id
    )
    history_use_case = ListTaskStatusHistoryUseCase(
        task_status_history_repository=task_status_history_repository,
        task_repository=task_repository,
    )
    history_command = ListTaskStatusHistoryCommand(task_id=task_id, limit=10, offset=0)
    result = await history_use_case.execute(command=history_command)
    assert result == []

    update_command = UpdateTaskCommand(task_id=task_id, status=TaskStatus.IN_PROGRESS)
    update_use_case = make_update_task_use_case(
        task_repository=task_repository,
        task_status_history_repository=task_status_history_repository,
        project_repository=project_repository,
    )
    await update_use_case.execute(command=update_command)
    result = await history_use_case.execute(command=history_command)
    assert len(result) == 1

    update_command = UpdateTaskCommand(task_id=task_id, status=TaskStatus.DONE)
    update_use_case = make_update_task_use_case(
        task_repository=task_repository,
        task_status_history_repository=task_status_history_repository,
        project_repository=project_repository,
    )
    await update_use_case.execute(command=update_command)
    result = await history_use_case.execute(command=history_command)
    assert len(result) == 2

    delete_command = DeleteTaskCommand(task_id=task_id)
    delete_use_case = make_delete_task_use_case(task_repository=task_repository)
    await delete_use_case.execute(command=delete_command)

    with pytest.raises(TaskNotFoundError):
        result = await history_use_case.execute(command=history_command)
        assert result == []


@pytest.mark.asyncio
async def test_task_status_history_not_found() -> None:
    task_status_history_repository = InMemoryTaskStatusHistoryRepository()
    task_repository = InMemoryTaskRepository()
    history_use_case = ListTaskStatusHistoryUseCase(
        task_status_history_repository=task_status_history_repository,
        task_repository=task_repository,
    )
    history_command = ListTaskStatusHistoryCommand(
        task_id=TEST_ID_GENERATOR.new_id(), limit=10, offset=0
    )
    with pytest.raises(TaskNotFoundError):
        await history_use_case.execute(command=history_command)
