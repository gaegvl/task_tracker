from datetime import datetime
from uuid import uuid4
import pytest
from src.application.use_cases.delete_project import (
    DeleteProjectCommand,
    DeleteProjectUseCase,
)
from src.domain.exceptions import (
    ProjectHasTasksError,
    ProjectNotFoundError,
)
from src.application.use_cases.delete_task import DeleteTaskCommand, DeleteTaskUseCase
from src.application.use_cases.purge_project import (
    PurgeProjectCommand,
    PurgeProjectUseCase,
)
from src.domain.entities.task import Task, TaskStatus
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
async def test_purge_project_cascade() -> None:
    project_repository = InMemoryProjectRepository()
    task_repository = InMemoryTaskRepository()
    project_id = await create_project_in_memory(project_repository)
    await add_tasks_to_repository(2, project_id, TaskStatus.TODO, task_repository)
    purge_project_use_case = PurgeProjectUseCase(project_repository, task_repository)
    command = PurgeProjectCommand(project_id=project_id)

    task_ids = [
        task.id
        for task in await task_repository.list_tasks(
            project_id=project_id, status=TaskStatus.TODO, limit=10, offset=0
        )
    ]
    delete_use_case = DeleteTaskUseCase(task_repository)

    for task_id in task_ids:
        delete_command = DeleteTaskCommand(task_id=task_id)
        await delete_use_case.execute(command=delete_command)

    delete_project_use_case = DeleteProjectUseCase(project_repository, task_repository)
    delete_command = DeleteProjectCommand(id=project_id)
    await delete_project_use_case.execute(command=delete_command)

    await purge_project_use_case.execute(command=command)

    with pytest.raises(ProjectNotFoundError):
        await project_repository.get_by_id(project_id)


@pytest.mark.asyncio
async def test_purge_project_with_active_tasks() -> None:
    project_repository = InMemoryProjectRepository()
    task_repository = InMemoryTaskRepository()
    project_id = await create_project_in_memory(project_repository)
    task_id = await create_task_in_memory(
        task_repository, project_repository, project_id
    )
    purge_project_use_case = PurgeProjectUseCase(project_repository, task_repository)
    command = PurgeProjectCommand(project_id=project_id)

    delete_task_use_case = DeleteTaskUseCase(task_repository)
    delete_command = DeleteTaskCommand(task_id=task_id)
    await delete_task_use_case.execute(command=delete_command)

    delete_project_use_case = DeleteProjectUseCase(project_repository, task_repository)
    delete_command = DeleteProjectCommand(id=project_id)
    await delete_project_use_case.execute(command=delete_command)

    task = Task(
        id=uuid4(),
        title="Test Task",
        description="Test Description",
        project_id=project_id,
        status=TaskStatus.TODO,
        created_at=datetime.now(),
        deleted_at=None,
    )
    await task_repository.add(task=task)

    with pytest.raises(ProjectHasTasksError):
        await purge_project_use_case.execute(command=command)


@pytest.mark.asyncio
async def test_purge_isolate_by_project_id() -> None:
    project_repository = InMemoryProjectRepository()
    task_repository = InMemoryTaskRepository()
    project_id_1 = await create_project_in_memory(project_repository)
    project_id_2 = await create_project_in_memory(project_repository)
    task_id_1 = await create_task_in_memory(
        task_repository, project_repository, project_id_1
    )
    task_id_2 = await create_task_in_memory(
        task_repository, project_repository, project_id_2
    )
    purge_project_use_case = PurgeProjectUseCase(project_repository, task_repository)

    delete_use_case = DeleteTaskUseCase(task_repository)
    delete_command = DeleteTaskCommand(task_id=task_id_1)
    await delete_use_case.execute(command=delete_command)

    delete_command = DeleteTaskCommand(task_id=task_id_2)
    await delete_use_case.execute(command=delete_command)

    command = PurgeProjectCommand(project_id=project_id_2)
    delete_project_use_case = DeleteProjectUseCase(project_repository, task_repository)
    delete_command = DeleteProjectCommand(id=project_id_2)
    await delete_project_use_case.execute(command=delete_command)

    await purge_project_use_case.execute(command=command)

    project_1 = await project_repository.get_by_id(project_id_1)

    assert project_1.id == project_id_1

    with pytest.raises(ProjectNotFoundError):
        await project_repository.get_by_id(project_id_2)
