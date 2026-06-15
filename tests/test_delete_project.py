import pytest

from src.application.use_cases.delete_project import (
    DeleteProjectCommand,
    DeleteProjectUseCase,
)
from src.application.use_cases.get_project_by_id import (
    GetProjectByIdCommand,
    GetProjectByIdUseCase,
)
from src.domain.exceptions import ProjectNotFoundError
from src.infrastructure.db.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)
from src.infrastructure.db.repositories.in_memory_task_repository import (
    InMemoryTaskRepository,
)
from tests.helpers import create_project_in_memory


@pytest.mark.asyncio
async def test_delete_project_use_case_removes_project() -> None:
    project_repository = InMemoryProjectRepository()
    task_repository = InMemoryTaskRepository()
    project_id = await create_project_in_memory(project_repository)
    delete_use_case = DeleteProjectUseCase(
        task_repository=task_repository, project_repository=project_repository
    )
    await delete_use_case.execute(command=DeleteProjectCommand(id=project_id))

    get_use_case = GetProjectByIdUseCase(project_repository=project_repository)

    with pytest.raises(ProjectNotFoundError):
        await get_use_case.execute(command=GetProjectByIdCommand(id=project_id))


@pytest.mark.asyncio
async def test_delete_project_use_case_not_found_on_second_delete() -> None:
    project_repository = InMemoryProjectRepository()
    task_repository = InMemoryTaskRepository()
    project_id = await create_project_in_memory(project_repository)
    delete_use_case = DeleteProjectUseCase(
        task_repository=task_repository, project_repository=project_repository
    )
    delete_command = DeleteProjectCommand(id=project_id)
    await delete_use_case.execute(command=delete_command)

    with pytest.raises(ProjectNotFoundError):
        await delete_use_case.execute(command=delete_command)
