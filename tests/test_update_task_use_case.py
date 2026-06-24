from datetime import datetime

import pytest

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
from tests.fakes import FixedClock
from tests.helpers import (
    TEST_ID_GENERATOR,
    create_project_in_memory,
    create_task_in_memory,
    make_update_task_use_case,
)

InMemoryTaskStatusHistoryRepository = (
    in_memory_task_status_history_repository.InMemoryTaskStatusHistoryRepository
)


@pytest.mark.asyncio
async def test_update_task_status_history_uses_clock_for_changed_at() -> None:
    fixed_at = datetime(2026, 6, 16, 12, 0, 0)
    clock = FixedClock(fixed_at)
    project_repository = InMemoryProjectRepository()
    project_id = await create_project_in_memory(project_repository)
    task_repository = InMemoryTaskRepository()
    task_id = await create_task_in_memory(
        task_repository, project_repository, project_id
    )
    task_status_history_repository = InMemoryTaskStatusHistoryRepository()
    update_use_case = make_update_task_use_case(
        task_repository=task_repository,
        project_repository=project_repository,
        task_status_history_repository=task_status_history_repository,
        clock=clock,
    )
    await update_use_case.execute(
        command=UpdateTaskCommand(task_id=task_id, status=TaskStatus.IN_PROGRESS)
    )
    history_use_case = ListTaskStatusHistoryUseCase(
        task_status_history_repository=task_status_history_repository,
        task_repository=task_repository,
    )
    history = await history_use_case.execute(
        command=ListTaskStatusHistoryCommand(task_id=task_id, limit=10, offset=0)
    )
    assert len(history) == 1
    assert history[0].changed_at == fixed_at


@pytest.mark.asyncio
async def test_update_task_use_case_todo_to_in_progress() -> None:
    project_repository = InMemoryProjectRepository()
    project_id = await create_project_in_memory(project_repository)
    task_repository = InMemoryTaskRepository()
    task_id = await create_task_in_memory(
        task_repository, project_repository, project_id
    )
    task_status_history_repository = InMemoryTaskStatusHistoryRepository()
    update_use_case = make_update_task_use_case(
        task_repository=task_repository,
        project_repository=project_repository,
        task_status_history_repository=task_status_history_repository,
    )
    updated_task = await update_use_case.execute(
        command=UpdateTaskCommand(task_id=task_id, status=TaskStatus.IN_PROGRESS)
    )

    assert updated_task.status == TaskStatus.IN_PROGRESS
    saved = await task_repository.get_by_id(task_id)
    assert saved.status == TaskStatus.IN_PROGRESS
    assert saved.title == "Test Task"
    assert saved.id == task_id
    assert saved.project_id == project_id
    assert saved.description == "Test Description"


@pytest.mark.asyncio
async def test_update_task_use_case_in_progress_to_done() -> None:
    project_repository = InMemoryProjectRepository()
    project_id = await create_project_in_memory(project_repository)
    task_repository = InMemoryTaskRepository()
    task_id = await create_task_in_memory(
        task_repository, project_repository, project_id
    )
    task_status_history_repository = InMemoryTaskStatusHistoryRepository()
    update_use_case = make_update_task_use_case(
        task_repository=task_repository,
        project_repository=project_repository,
        task_status_history_repository=task_status_history_repository,
    )
    await update_use_case.execute(
        command=UpdateTaskCommand(task_id=task_id, status=TaskStatus.IN_PROGRESS)
    )

    updated_task = await update_use_case.execute(
        command=UpdateTaskCommand(task_id=task_id, status=TaskStatus.DONE)
    )

    assert updated_task.status == TaskStatus.DONE


@pytest.mark.asyncio
async def test_update_task_use_case_not_found() -> None:
    project_repository = InMemoryProjectRepository()
    task_repository = InMemoryTaskRepository()
    task_status_history_repository = InMemoryTaskStatusHistoryRepository()
    update_use_case = make_update_task_use_case(
        task_repository=task_repository,
        project_repository=project_repository,
        task_status_history_repository=task_status_history_repository,
    )

    with pytest.raises(TaskNotFoundError):
        await update_use_case.execute(
            command=UpdateTaskCommand(
                task_id=TEST_ID_GENERATOR.new_id(), status=TaskStatus.IN_PROGRESS
            )
        )


@pytest.mark.asyncio
async def test_update_task_use_case_invalid_transition_todo_to_done() -> None:
    project_repository = InMemoryProjectRepository()
    project_id = await create_project_in_memory(project_repository)
    task_repository = InMemoryTaskRepository()
    task_id = await create_task_in_memory(
        task_repository, project_repository, project_id
    )
    task_status_history_repository = InMemoryTaskStatusHistoryRepository()
    update_use_case = make_update_task_use_case(
        task_repository=task_repository,
        project_repository=project_repository,
        task_status_history_repository=task_status_history_repository,
    )

    with pytest.raises(InvalidTaskStatusTransitionError):
        await update_use_case.execute(
            command=UpdateTaskCommand(task_id=task_id, status=TaskStatus.DONE)
        )


@pytest.mark.asyncio
async def test_update_task_use_case_valid_transition_in_progress_to_todo() -> None:
    project_repository = InMemoryProjectRepository()
    project_id = await create_project_in_memory(project_repository)
    task_repository = InMemoryTaskRepository()
    task_id = await create_task_in_memory(
        task_repository, project_repository, project_id
    )
    task_status_history_repository = InMemoryTaskStatusHistoryRepository()
    update_use_case = make_update_task_use_case(
        task_repository=task_repository,
        project_repository=project_repository,
        task_status_history_repository=task_status_history_repository,
    )
    await update_use_case.execute(
        command=UpdateTaskCommand(task_id=task_id, status=TaskStatus.IN_PROGRESS)
    )

    updated_task = await update_use_case.execute(
        command=UpdateTaskCommand(task_id=task_id, status=TaskStatus.TODO)
    )

    assert updated_task.status == TaskStatus.TODO


@pytest.mark.asyncio
async def test_update_task_use_case_invalid_transition_done_to_in_progress() -> None:
    project_repository = InMemoryProjectRepository()
    project_id = await create_project_in_memory(project_repository)
    task_repository = InMemoryTaskRepository()
    task_id = await create_task_in_memory(
        task_repository, project_repository, project_id
    )
    task_status_history_repository = InMemoryTaskStatusHistoryRepository()
    update_use_case = make_update_task_use_case(
        task_repository=task_repository,
        project_repository=project_repository,
        task_status_history_repository=task_status_history_repository,
    )
    await update_use_case.execute(
        command=UpdateTaskCommand(task_id=task_id, status=TaskStatus.IN_PROGRESS)
    )
    await update_use_case.execute(
        command=UpdateTaskCommand(task_id=task_id, status=TaskStatus.DONE)
    )

    with pytest.raises(InvalidTaskStatusTransitionError):
        await update_use_case.execute(
            command=UpdateTaskCommand(task_id=task_id, status=TaskStatus.IN_PROGRESS)
        )


@pytest.mark.asyncio
async def test_update_task_use_case_invalid_transition_done_to_todo() -> None:
    project_repository = InMemoryProjectRepository()
    project_id = await create_project_in_memory(project_repository)
    task_repository = InMemoryTaskRepository()
    task_id = await create_task_in_memory(
        task_repository, project_repository, project_id
    )
    task_status_history_repository = InMemoryTaskStatusHistoryRepository()
    update_use_case = make_update_task_use_case(
        task_repository=task_repository,
        project_repository=project_repository,
        task_status_history_repository=task_status_history_repository,
    )
    await update_use_case.execute(
        command=UpdateTaskCommand(task_id=task_id, status=TaskStatus.IN_PROGRESS)
    )
    await update_use_case.execute(
        command=UpdateTaskCommand(task_id=task_id, status=TaskStatus.DONE)
    )

    with pytest.raises(InvalidTaskStatusTransitionError):
        await update_use_case.execute(
            command=UpdateTaskCommand(task_id=task_id, status=TaskStatus.TODO)
        )


@pytest.mark.asyncio
async def test_update_task_use_case_same_status_is_allowed() -> None:
    project_repository = InMemoryProjectRepository()
    project_id = await create_project_in_memory(project_repository)
    task_repository = InMemoryTaskRepository()
    task_id = await create_task_in_memory(
        task_repository, project_repository, project_id
    )
    task_status_history_repository = InMemoryTaskStatusHistoryRepository()
    update_use_case = make_update_task_use_case(
        task_repository=task_repository,
        project_repository=project_repository,
        task_status_history_repository=task_status_history_repository,
    )
    await update_use_case.execute(
        command=UpdateTaskCommand(task_id=task_id, status=TaskStatus.IN_PROGRESS)
    )
    await update_use_case.execute(
        command=UpdateTaskCommand(task_id=task_id, status=TaskStatus.DONE)
    )

    updated_task = await update_use_case.execute(
        command=UpdateTaskCommand(task_id=task_id, status=TaskStatus.DONE)
    )

    assert updated_task.status == TaskStatus.DONE
