import pytest

from src.application.use_cases.delete_project import DeleteProjectCommand
from src.application.use_cases.delete_task import DeleteTaskCommand
from src.application.use_cases.get_project_by_id import (
    GetProjectByIdCommand,
    GetProjectByIdUseCase,
)
from src.application.use_cases.list_projects import (
    ListProjectsCommand,
    ListProjectsUseCase,
)
from src.domain.exceptions import (
    ProjectHasTasksError,
    ProjectNotFoundError,
    TaskNotFoundError,
)
from src.infrastructure.db.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)
from src.infrastructure.db.repositories.in_memory_task_repository import (
    InMemoryTaskRepository,
)
from tests.helpers import (
    create_project_in_memory,
    create_task_in_memory,
    make_delete_project_use_case,
    make_delete_task_use_case,
)


@pytest.mark.asyncio
async def test_delete_project_use_case_removes_project() -> None:
    project_repository = InMemoryProjectRepository()
    task_repository = InMemoryTaskRepository()
    project_id = await create_project_in_memory(project_repository)
    delete_use_case = make_delete_project_use_case(
        project_repository=project_repository,
        task_repository=task_repository,
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
    delete_use_case = make_delete_project_use_case(
        project_repository=project_repository,
        task_repository=task_repository,
    )
    delete_command = DeleteProjectCommand(id=project_id)
    await delete_use_case.execute(command=delete_command)

    with pytest.raises(ProjectNotFoundError):
        await delete_use_case.execute(command=delete_command)


@pytest.mark.asyncio
async def test_delete_project_list_projects_does_not_contain_project() -> None:
    project_repository = InMemoryProjectRepository()
    task_repository = InMemoryTaskRepository()
    project_id_1 = await create_project_in_memory(project_repository)
    await create_project_in_memory(project_repository)
    await create_project_in_memory(project_repository)

    delete_use_case = make_delete_project_use_case(
        project_repository=project_repository,
        task_repository=task_repository,
    )
    delete_command = DeleteProjectCommand(id=project_id_1)
    await delete_use_case.execute(command=delete_command)

    list_projects_use_case = ListProjectsUseCase(project_repository=project_repository)
    result = await list_projects_use_case.execute(
        command=ListProjectsCommand(limit=10, offset=0)
    )

    assert project_id_1 not in [project.id for project in result]
    assert len(result) == 2


@pytest.mark.asyncio
async def test_delete_project_with_tasks_raises_project_has_tasks_error() -> None:
    project_repository = InMemoryProjectRepository()
    task_repository = InMemoryTaskRepository()
    project_id = await create_project_in_memory(project_repository)
    await create_task_in_memory(task_repository, project_repository, project_id)
    delete_use_case = make_delete_project_use_case(
        project_repository=project_repository,
        task_repository=task_repository,
    )
    with pytest.raises(ProjectHasTasksError):
        await delete_use_case.execute(command=DeleteProjectCommand(id=project_id))


@pytest.mark.asyncio
async def test_soft_delete_project_with_soft_deleted_tasks() -> None:
    project_repository = InMemoryProjectRepository()
    task_repository = InMemoryTaskRepository()
    project_id = await create_project_in_memory(project_repository)
    task_id = await create_task_in_memory(
        task_repository, project_repository, project_id
    )
    delete_task_use_case = make_delete_task_use_case(task_repository=task_repository)
    delete_task_command = DeleteTaskCommand(task_id)

    await delete_task_use_case.execute(command=delete_task_command)

    with pytest.raises(TaskNotFoundError):
        await task_repository.get_by_id(task_id)

    delete_project_use_case = make_delete_project_use_case(
        project_repository=project_repository,
        task_repository=task_repository,
    )
    delete_project_command = DeleteProjectCommand(id=project_id)
    await delete_project_use_case.execute(command=delete_project_command)
    with pytest.raises(ProjectNotFoundError):
        await project_repository.get_by_id(project_id)
