from datetime import datetime
import pytest

from src.application.use_cases.create_task import CreateTaskCommand, CreateTaskUseCase
from src.application.use_cases.list_tasks import ListTasksCommand, ListTaskUseCase
from src.domain.entities.task import Task, TaskStatus
from src.infrastructure.db.repositories.in_memory_task_repository import (
    InMemoryTaskRepository,
)
from uuid import UUID, uuid4


async def create_some_tasks(
    i: int, project_id: UUID, status: TaskStatus, repository: InMemoryTaskRepository
) -> None:
    for i in range(i):
        id = uuid4()
        task = Task(
            id=id,
            title=f"Test Task {i}",
            description=f"Test Description {i}",
            project_id=project_id,
            status=status,
            created_at=datetime.now(),
        )
        await repository.add(task=task)


@pytest.mark.asyncio
async def test_get_list_task_use_case() -> None:
    project_id_todo = uuid4()
    project_id_in_progress = uuid4()
    project_id_done = uuid4()

    repository = InMemoryTaskRepository()

    create_task = CreateTaskUseCase(repository)

    await create_task.execute(
        command=CreateTaskCommand(
            title="Test Task",
            description="Test Description",
            project_id=project_id_todo,
        )
    )

    await create_some_tasks(
        15, project_id_in_progress, TaskStatus.IN_PROGRESS, repository
    )
    await create_some_tasks(3, project_id_done, TaskStatus.DONE, repository)

    create_use_case = ListTaskUseCase(repository)
    command = ListTasksCommand(
        project_id=project_id_todo, status=TaskStatus.TODO, limit=3, offset=0
    )
    result = await create_use_case.execute(command=command)
    assert len(result.items) == 1
    assert result.items[0].status == TaskStatus.TODO

    command = ListTasksCommand(
        project_id=project_id_in_progress,
        status=TaskStatus.IN_PROGRESS,
        limit=10,
        offset=0,
    )
    result = await create_use_case.execute(command=command)
    assert len(result.items) == 10
    assert result.items[0].status == TaskStatus.IN_PROGRESS

    command = ListTasksCommand(
        project_id=project_id_in_progress,
        status=TaskStatus.IN_PROGRESS,
        limit=10,
        offset=10,
    )
    result = await create_use_case.execute(command=command)
    assert len(result.items) == 5
    assert result.items[0].status == TaskStatus.IN_PROGRESS

    command = ListTasksCommand(
        project_id=project_id_done, status=TaskStatus.DONE, limit=3, offset=0
    )
    result = await create_use_case.execute(command=command)
    assert len(result.items) == 3
    assert result.items[0].status == TaskStatus.DONE
