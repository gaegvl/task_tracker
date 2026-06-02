import pytest
from src.application.use_cases.create_project import (
    CreateProjectCommand,
    CreateProjectUseCase,
)
from src.infrastructure.db.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)
from src.application.use_cases.create_task import CreateTaskCommand, CreateTaskUseCase
from src.application.use_cases.delete_task import DeleteTaskCommand, DeleteTaskUseCase
from src.domain.exceptions import TaskNotFoundError
from src.infrastructure.db.repositories.in_memory_task_repository import (
    InMemoryTaskRepository,
)
from uuid import uuid4


@pytest.mark.asyncio
async def test_delete_task_use_case_success() -> None:
    repository = InMemoryTaskRepository()
    project_repository = InMemoryProjectRepository()
    project_create_use_case = CreateProjectUseCase(project_repository)
    project_command = CreateProjectCommand(
        name="Test Project", description="Test Description"
    )
    project_result = await project_create_use_case.execute(command=project_command)
    create_task = CreateTaskUseCase(repository, project_repository)

    create_command = CreateTaskCommand(
        title="Test Task", description="Test Description", project_id=project_result.id
    )
    create_task_result = await create_task.execute(command=create_command)

    task = await repository.get_by_id(create_task_result.id)

    assert task is not None

    delete_task = DeleteTaskUseCase(repository)
    delete_command = DeleteTaskCommand(task_id=task.id)

    await delete_task.execute(command=delete_command)

    with pytest.raises(TaskNotFoundError):
        await repository.get_by_id(task.id)


@pytest.mark.asyncio
async def test_delete_task_use_case_not_found() -> None:
    repository = InMemoryTaskRepository()
    delete_task = DeleteTaskUseCase(repository)
    delete_command = DeleteTaskCommand(task_id=uuid4())

    with pytest.raises(TaskNotFoundError):
        await delete_task.execute(command=delete_command)
