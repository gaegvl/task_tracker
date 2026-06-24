import pytest

from src.application.use_cases.create_project import CreateProjectCommand
from src.application.use_cases.list_projects import (
    ListProjectsCommand,
    ListProjectsUseCase,
)
from src.infrastructure.db.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)
from tests.helpers import make_create_project_use_case


@pytest.mark.asyncio
async def test_get_list_project_use_case() -> None:
    repository = InMemoryProjectRepository()
    create_use_case = make_create_project_use_case(project_repository=repository)
    command = CreateProjectCommand(
        name="Test Project 1", description="Test Description"
    )
    result1 = await create_use_case.execute(command=command)

    command = CreateProjectCommand(
        name="Test Project 2", description="Test Description"
    )
    await create_use_case.execute(command=command)

    command = CreateProjectCommand(
        name="Test Project 3", description="Test Description"
    )
    await create_use_case.execute(command=command)

    get_list_use_case = ListProjectsUseCase(project_repository=repository)
    get_list_command = ListProjectsCommand(limit=10, offset=0)
    get_list_result = await get_list_use_case.execute(command=get_list_command)

    assert len(get_list_result) == 3
    assert get_list_result[0].id == result1.id
    assert get_list_result[0].name == "Test Project 1"
    assert get_list_result[0].description == "Test Description"
