import pytest

from src.application.use_cases.list_tasks import ListTasksCommand, ListTaskUseCase
from src.domain.entities.task import TaskStatus
from src.infrastructure.db.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)
from src.infrastructure.db.repositories.in_memory_task_repository import (
    InMemoryTaskRepository,
)
from tests.helpers import (
    add_tasks_to_repository,
    create_project_in_memory,
    create_task_in_memory,
)


@pytest.mark.asyncio
async def test_list_tasks_filters_by_project_id_and_status_todo() -> None:
    project_repository = InMemoryProjectRepository()
    project_id_todo = await create_project_in_memory(
        project_repository, name="project_id_todo"
    )
    project_id_in_progress = await create_project_in_memory(
        project_repository, name="project_id_in_progress"
    )
    task_repository = InMemoryTaskRepository()
    await create_task_in_memory(task_repository, project_repository, project_id_todo)
    await add_tasks_to_repository(
        15, project_id_in_progress, TaskStatus.IN_PROGRESS, task_repository
    )

    use_case = ListTaskUseCase(task_repository)
    result = await use_case.execute(
        command=ListTasksCommand(
            project_id=project_id_todo, status=TaskStatus.TODO, limit=3, offset=0
        )
    )

    assert len(result.items) == 1
    assert result.items[0].status == TaskStatus.TODO


@pytest.mark.asyncio
async def test_list_tasks_filters_by_project_id_and_status_in_progress() -> None:
    project_repository = InMemoryProjectRepository()
    project_id_todo = await create_project_in_memory(
        project_repository, name="project_id_todo"
    )
    project_id_in_progress = await create_project_in_memory(
        project_repository, name="project_id_in_progress"
    )
    task_repository = InMemoryTaskRepository()
    await create_task_in_memory(task_repository, project_repository, project_id_todo)
    await add_tasks_to_repository(
        15, project_id_in_progress, TaskStatus.IN_PROGRESS, task_repository
    )

    use_case = ListTaskUseCase(task_repository)
    result = await use_case.execute(
        command=ListTasksCommand(
            project_id=project_id_in_progress,
            status=TaskStatus.IN_PROGRESS,
            limit=10,
            offset=0,
        )
    )

    assert len(result.items) == 10
    assert result.items[0].status == TaskStatus.IN_PROGRESS


@pytest.mark.asyncio
async def test_list_tasks_pagination_offset() -> None:
    project_repository = InMemoryProjectRepository()
    project_id_in_progress = await create_project_in_memory(
        project_repository, name="project_id_in_progress"
    )
    task_repository = InMemoryTaskRepository()
    await add_tasks_to_repository(
        15, project_id_in_progress, TaskStatus.IN_PROGRESS, task_repository
    )

    use_case = ListTaskUseCase(task_repository)
    result = await use_case.execute(
        command=ListTasksCommand(
            project_id=project_id_in_progress,
            status=TaskStatus.IN_PROGRESS,
            limit=10,
            offset=10,
        )
    )

    assert len(result.items) == 5
    assert result.items[0].status == TaskStatus.IN_PROGRESS


@pytest.mark.asyncio
async def test_list_tasks_filters_by_project_id_and_status_done() -> None:
    project_repository = InMemoryProjectRepository()
    project_id_done = await create_project_in_memory(
        project_repository, name="project_id_done"
    )
    task_repository = InMemoryTaskRepository()
    await add_tasks_to_repository(3, project_id_done, TaskStatus.DONE, task_repository)

    use_case = ListTaskUseCase(task_repository)
    result = await use_case.execute(
        command=ListTasksCommand(
            project_id=project_id_done, status=TaskStatus.DONE, limit=3, offset=0
        )
    )

    assert len(result.items) == 3
    assert result.items[0].status == TaskStatus.DONE
