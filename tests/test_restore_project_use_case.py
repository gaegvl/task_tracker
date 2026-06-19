from uuid import uuid4
import pytest

from src.application.use_cases.delete_project import (
    DeleteProjectCommand,
    DeleteProjectUseCase,
)
from src.application.use_cases.restore_project import (
    RestoreProjectCommand,
    RestoreProjectUseCase,
)
from src.domain.entities.task import TaskStatus
from src.domain.exceptions import ProjectNotFoundError
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
async def test_restore_project_use_case() -> None:
    project_repository = InMemoryProjectRepository()
    task_repository = InMemoryTaskRepository()
    project_id = await create_project_in_memory(project_repository)
    await project_repository.delete(project_id)
    use_case = RestoreProjectUseCase(
        project_repository=project_repository, task_repository=task_repository
    )
    command = RestoreProjectCommand(project_id=project_id)
    await use_case.execute(command=command)
    result = await project_repository.get_by_id(project_id)
    assert result.id == project_id
    assert result.deleted_at is None


@pytest.mark.asyncio
async def test_restore_not_found_project() -> None:
    project_repository = InMemoryProjectRepository()
    task_repository = InMemoryTaskRepository()
    use_case = RestoreProjectUseCase(
        project_repository=project_repository, task_repository=task_repository
    )
    command = RestoreProjectCommand(project_id=uuid4())
    with pytest.raises(ProjectNotFoundError):
        await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_restore_active_project() -> None:
    project_repository = InMemoryProjectRepository()
    task_repository = InMemoryTaskRepository()
    project_id = await create_project_in_memory(project_repository)
    use_case = RestoreProjectUseCase(
        project_repository=project_repository, task_repository=task_repository
    )
    command = RestoreProjectCommand(project_id=project_id)
    with pytest.raises(ProjectNotFoundError):
        await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_restore_project_with_tasks() -> None:
    project_repository = InMemoryProjectRepository()
    task_repository = InMemoryTaskRepository()
    project_id = await create_project_in_memory(project_repository)
    await add_tasks_to_repository(3, project_id, TaskStatus.TODO, task_repository)
    task_ids = [
        task.id
        for task in await task_repository.list_tasks(
            project_id=project_id, status=None, limit=10, offset=0
        )
    ]
    for task_id in task_ids:
        await task_repository.delete(task_id)

    command = DeleteProjectCommand(id=project_id)
    use_case = DeleteProjectUseCase(
        project_repository=project_repository, task_repository=task_repository
    )
    await use_case.execute(command=command)
    use_case = RestoreProjectUseCase(
        project_repository=project_repository, task_repository=task_repository
    )
    command = RestoreProjectCommand(project_id=project_id)
    await use_case.execute(command=command)
    result = await project_repository.get_by_id(project_id)
    assert result.id == project_id
    result = await task_repository.list_tasks(
        project_id=project_id, status=None, limit=10, offset=0
    )
    assert len(result) == 3
    for task in result:
        assert task.deleted_at is None


@pytest.mark.asyncio
async def test_isolate_restore_project_with_tasks() -> None:
    project_repository = InMemoryProjectRepository()
    task_repository = InMemoryTaskRepository()
    project_id_1 = await create_project_in_memory(project_repository)
    project_id_2 = await create_project_in_memory(project_repository)

    task_id_1 = await create_task_in_memory(
        task_repository, project_repository, project_id_1
    )
    await project_repository.delete(project_id_1)
    await project_repository.delete(project_id_2)

    await task_repository.delete(task_id_1)

    use_case = RestoreProjectUseCase(
        project_repository=project_repository, task_repository=task_repository
    )
    command = RestoreProjectCommand(project_id=project_id_1)
    await use_case.execute(command=command)

    result = await project_repository.get_by_id(project_id_1)
    assert result.id == project_id_1
    assert result.deleted_at is None
    result = await task_repository.list_tasks(
        project_id=project_id_1, status=None, limit=10, offset=0
    )
    assert len(result) == 1
    assert result[0].id == task_id_1
    assert result[0].deleted_at is None

    with pytest.raises(ProjectNotFoundError):
        await project_repository.get_by_id(project_id_2)
