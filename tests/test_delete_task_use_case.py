import pytest

from src.application.use_cases.create_task import CreateTaskCommand
from src.application.use_cases.delete_task import DeleteTaskCommand
from src.domain.exceptions import TaskNotFoundError
from src.infrastructure.db.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)
from src.infrastructure.db.repositories.in_memory_task_repository import (
    InMemoryTaskRepository,
)
from tests.helpers import (
    TEST_ID_GENERATOR,
    create_project_in_memory,
    create_task_in_memory,
    make_create_task_use_case,
    make_delete_task_use_case,
)


@pytest.mark.asyncio
async def test_delete_task_use_case_not_found() -> None:
    repository = InMemoryTaskRepository()
    delete_task = make_delete_task_use_case(task_repository=repository)

    with pytest.raises(TaskNotFoundError):
        await delete_task.execute(
            command=DeleteTaskCommand(task_id=TEST_ID_GENERATOR.new_id())
        )


@pytest.mark.asyncio
async def test_delete_task_use_case_soft_deleted_not_found_on_get() -> None:
    project_repository = InMemoryProjectRepository()
    project_id = await create_project_in_memory(project_repository)
    task_repository = InMemoryTaskRepository()
    task_id = await create_task_in_memory(
        task_repository, project_repository, project_id
    )
    delete_use_case = make_delete_task_use_case(task_repository=task_repository)
    await delete_use_case.execute(command=DeleteTaskCommand(task_id=task_id))

    with pytest.raises(TaskNotFoundError):
        await task_repository.get_by_id(task_id)


@pytest.mark.asyncio
async def test_delete_task_use_case_soft_deleted_raises_on_second_delete() -> None:
    project_repository = InMemoryProjectRepository()
    project_id = await create_project_in_memory(project_repository)
    task_repository = InMemoryTaskRepository()
    task_id = await create_task_in_memory(
        task_repository, project_repository, project_id
    )
    delete_use_case = make_delete_task_use_case(task_repository=task_repository)
    delete_command = DeleteTaskCommand(task_id=task_id)
    await delete_use_case.execute(command=delete_command)

    with pytest.raises(TaskNotFoundError):
        await delete_use_case.execute(command=delete_command)


@pytest.mark.asyncio
async def test_delete_task_use_case_soft_deleted_excluded_from_list() -> None:
    project_repository = InMemoryProjectRepository()
    project_id = await create_project_in_memory(project_repository)
    task_repository = InMemoryTaskRepository()
    create_use_case = make_create_task_use_case(
        task_repository=task_repository,
        project_repository=project_repository,
    )
    task_result_1 = await create_use_case.execute(
        command=CreateTaskCommand(
            title="Test Task", description="Test Description", project_id=project_id
        )
    )
    await create_use_case.execute(
        command=CreateTaskCommand(
            title="Test Task 2",
            description="Test Description 2",
            project_id=project_id,
        )
    )
    await create_use_case.execute(
        command=CreateTaskCommand(
            title="Test Task 3",
            description="Test Description 3",
            project_id=project_id,
        )
    )
    delete_use_case = make_delete_task_use_case(task_repository=task_repository)
    await delete_use_case.execute(command=DeleteTaskCommand(task_id=task_result_1.id))

    tasks = await task_repository.list_tasks(
        project_id=project_id, status=None, limit=10, offset=0
    )

    assert len(tasks) == 2
