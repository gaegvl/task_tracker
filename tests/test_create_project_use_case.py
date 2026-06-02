import pytest

from src.application.use_cases.create_project import (
    CreateProjectCommand,
    CreateProjectUseCase,
)
from src.infrastructure.db.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)


@pytest.mark.asyncio
async def test_create_project_use_case_success() -> None:
    repository = InMemoryProjectRepository()
    use_case = CreateProjectUseCase(project_repository=repository)
    command = CreateProjectCommand(name="Test Project", description="Test Description")
    result = await use_case.execute(command=command)

    assert result.id is not None
    assert result.name == "Test Project"
    assert result.description == "Test Description"
