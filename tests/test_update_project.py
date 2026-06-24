import pytest

from src.application.use_cases.create_project import CreateProjectCommand
from src.application.use_cases.update_project import (
    UpdateProjectCommand,
    UpdateProjectUseCase,
)
from src.infrastructure.db.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)
from tests.helpers import make_create_project_use_case


@pytest.mark.asyncio
async def update_project_use_case() -> None:
    repository = InMemoryProjectRepository()
    create_use_case = make_create_project_use_case(project_repository=repository)
    command = CreateProjectCommand(name="Test Project", description="Test Description")
    result = await create_use_case.execute(command=command)

    update_use_case = UpdateProjectUseCase(project_repository=repository)
    update_command = UpdateProjectCommand(
        id=result.id, name="Updated Project", description="Updated Description"
    )
    updated_result = await update_use_case.execute(command=update_command)

    assert updated_result.id == result.id
    assert updated_result.name == "Updated Project"
    assert updated_result.description == "Updated Description"
