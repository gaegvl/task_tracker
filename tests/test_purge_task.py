import pytest

from src.application.use_cases.get_task_by_id import (
    GetTaskByIdCommand,
    GetTaskByIdUseCase,
)
from src.application.use_cases.delete_task import DeleteTaskCommand, DeleteTaskUseCase
from src.application.use_cases.purge_task import PurgeTaskCommand, PurgeTaskUseCase
from src.domain.exceptions import TaskNotFoundError
from src.infrastructure.db.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)
from src.infrastructure.db.repositories.in_memory_task_repository import (
    InMemoryTaskRepository,
)
from tests.helpers import create_project_in_memory, create_task_in_memory


@pytest.mark.asyncio
async def test_purge_active_task() -> None:
    task_repository = InMemoryTaskRepository()
    project_repository = InMemoryProjectRepository()
    project_id = await create_project_in_memory(project_repository)
    task_id = await create_task_in_memory(
        task_repository, project_repository, project_id
    )
    purge_task_use_case = PurgeTaskUseCase(task_repository)
    command = PurgeTaskCommand(task_id=task_id)
    with pytest.raises(TaskNotFoundError):
        await purge_task_use_case.execute(command=command)


@pytest.mark.asyncio
async def test_purge_soft_deleted_task() -> None:
    task_repository = InMemoryTaskRepository()
    project_repository = InMemoryProjectRepository()
    project_id = await create_project_in_memory(project_repository)
    task_id = await create_task_in_memory(
        task_repository, project_repository, project_id
    )
    purge_task_use_case = PurgeTaskUseCase(task_repository)
    command = PurgeTaskCommand(task_id=task_id)

    delete_use_case = DeleteTaskUseCase(task_repository)
    delete_command = DeleteTaskCommand(task_id=task_id)
    await delete_use_case.execute(command=delete_command)

    await purge_task_use_case.execute(command=command)

    get_task_by_id_use_case = GetTaskByIdUseCase(task_repository)
    get_command = GetTaskByIdCommand(id=task_id)
    with pytest.raises(TaskNotFoundError):
        await get_task_by_id_use_case.execute(command=get_command)
