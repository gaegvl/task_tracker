import pytest
from src.infrastructure.db.repositories.in_memory_task_repository import (
    InMemoryTaskRepository,
)
from src.application.use_cases.get_project_by_id import (
    GetProjectByIdCommand,
    GetProjectByIdUseCase,
)
from src.application.use_cases.create_project import (
    CreateProjectCommand,
    CreateProjectUseCase,
)
from src.application.use_cases.delete_project import (
    DeleteProjectCommand,
    DeleteProjectUseCase,
)
from src.infrastructure.db.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)
from src.domain.exceptions import ProjectNotFoundError


@pytest.mark.asyncio
async def test_delete_project_use_case() -> None:
    repository = InMemoryProjectRepository()
    task_repository = InMemoryTaskRepository()
    create_use_case = CreateProjectUseCase(project_repository=repository)
    command = CreateProjectCommand(name="Test Project", description="Test Description")
    result = await create_use_case.execute(command=command)

    delete_use_case = DeleteProjectUseCase(
        task_repository=task_repository, project_repository=repository
    )
    delete_command = DeleteProjectCommand(id=result.id)
    await delete_use_case.execute(command=delete_command)

    get_use_case = GetProjectByIdUseCase(project_repository=repository)
    get_command = GetProjectByIdCommand(id=result.id)

    with pytest.raises(ProjectNotFoundError):
        await get_use_case.execute(command=get_command)

    with pytest.raises(ProjectNotFoundError):
        await delete_use_case.execute(command=delete_command)
