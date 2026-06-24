import pytest

from src.application.use_cases.create_project import CreateProjectCommand
from src.application.use_cases.get_project_by_id import (
    GetProjectByIdCommand,
    GetProjectByIdUseCase,
)
from src.infrastructure.db.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)
from tests.helpers import make_create_project_use_case


@pytest.mark.asyncio
async def test_get_project_by_id_use_case() -> None:
    repository = InMemoryProjectRepository()
    use_case = make_create_project_use_case(project_repository=repository)
    commnad = CreateProjectCommand(name="Test Project", description="Test Description")
    result = await use_case.execute(command=commnad)

    get_use_case = GetProjectByIdUseCase(project_repository=repository)
    get_command = GetProjectByIdCommand(id=result.id)
    get_result = await get_use_case.execute(command=get_command)
    assert get_result.id == result.id
    assert get_result.name == "Test Project"
    assert get_result.description == "Test Description"
