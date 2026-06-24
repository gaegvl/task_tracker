import pytest

from src.application.use_cases.create_project import CreateProjectCommand
from src.infrastructure.db.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)
from tests.helpers import make_create_project_use_case


@pytest.mark.asyncio
async def test_create_project_use_case_success() -> None:
    repository = InMemoryProjectRepository()
    use_case = make_create_project_use_case(project_repository=repository)
    command = CreateProjectCommand(name="Test Project", description="Test Description")
    result = await use_case.execute(command=command)

    assert result.id is not None
