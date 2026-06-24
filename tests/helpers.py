from datetime import datetime
from uuid import UUID

from fastapi.testclient import TestClient

from src.application.ports.clock import ClockPort
from src.application.ports.id_generator import IdGeneratorPort
from src.application.ports.project_repository import ProjectRepositoryPort
from src.application.ports.task_repository import TaskRepositoryPort
from src.application.ports.task_status_history_repository import (
    TaskStatusHistoryRepositoryPort,
)
from src.application.use_cases.create_project import (
    CreateProjectCommand,
    CreateProjectUseCase,
)
from src.application.use_cases.create_task import CreateTaskCommand, CreateTaskUseCase
from src.application.use_cases.delete_project import DeleteProjectUseCase
from src.application.use_cases.delete_task import DeleteTaskUseCase
from src.application.use_cases.update_task import UpdateTaskUseCase
from src.domain.entities.project import Project
from src.domain.entities.task import Task, TaskStatus
from src.infrastructure.db.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)
from src.infrastructure.db.repositories.in_memory_task_repository import (
    InMemoryTaskRepository,
)
from src.infrastructure.id_generator.system_id_generator import SystemIdGenerator
from tests.fakes import FixedClock

TEST_CLOCK = FixedClock(datetime(2026, 1, 1, 12, 0, 0))
TEST_ID_GENERATOR = SystemIdGenerator()


def make_create_project_use_case(
    project_repository: ProjectRepositoryPort,
    clock: ClockPort = TEST_CLOCK,
    id_generator: IdGeneratorPort = TEST_ID_GENERATOR,
) -> CreateProjectUseCase:
    return CreateProjectUseCase(project_repository, clock, id_generator)


def make_create_task_use_case(
    task_repository: TaskRepositoryPort,
    project_repository: ProjectRepositoryPort,
    clock: ClockPort = TEST_CLOCK,
    id_generator: IdGeneratorPort = TEST_ID_GENERATOR,
) -> CreateTaskUseCase:
    return CreateTaskUseCase(task_repository, project_repository, clock, id_generator)


def make_update_task_use_case(
    task_repository: TaskRepositoryPort,
    project_repository: ProjectRepositoryPort,
    task_status_history_repository: TaskStatusHistoryRepositoryPort,
    clock: ClockPort = TEST_CLOCK,
    id_generator: IdGeneratorPort = TEST_ID_GENERATOR,
) -> UpdateTaskUseCase:
    return UpdateTaskUseCase(
        task_repository,
        project_repository,
        task_status_history_repository,
        clock,
        id_generator,
    )


def make_delete_task_use_case(
    task_repository: TaskRepositoryPort,
    clock: ClockPort = TEST_CLOCK,
) -> DeleteTaskUseCase:
    return DeleteTaskUseCase(task_repository, clock)


def make_delete_project_use_case(
    project_repository: ProjectRepositoryPort,
    task_repository: TaskRepositoryPort,
    clock: ClockPort = TEST_CLOCK,
) -> DeleteProjectUseCase:
    return DeleteProjectUseCase(project_repository, task_repository, clock)


def create_project_via_api(
    client: TestClient,
    name: str = "Test Project",
    description: str = "Test Description",
) -> UUID:
    response = client.post(
        "/projects",
        json={"name": name, "description": description},
    )
    assert response.status_code == 201
    return response.json()["id"]


def create_task_via_api(
    client: TestClient,
    project_id: UUID,
    title: str = "Test Task",
    description: str = "Test Description",
) -> UUID:
    response = client.post(
        "/tasks",
        json={
            "title": title,
            "description": description,
            "project_id": str(project_id),
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def create_tasks_via_api(
    client: TestClient, count: int, project_id: UUID
) -> list[UUID]:
    return [
        create_task_via_api(
            client,
            project_id,
            title=f"Test Task {index}",
            description=f"Test Description {index}",
        )
        for index in range(count)
    ]


async def create_project_in_memory(
    repository: InMemoryProjectRepository,
    name: str = "Test Project",
    description: str = "Test Description",
) -> UUID:
    use_case = make_create_project_use_case(project_repository=repository)
    command = CreateProjectCommand(name=name, description=description)
    result = await use_case.execute(command=command)
    return result.id


async def create_task_in_memory(
    task_repository: InMemoryTaskRepository,
    project_repository: InMemoryProjectRepository,
    project_id: UUID,
    title: str = "Test Task",
    description: str = "Test Description",
) -> UUID:
    use_case = make_create_task_use_case(
        task_repository=task_repository,
        project_repository=project_repository,
    )
    result = await use_case.execute(
        command=CreateTaskCommand(
            title=title, description=description, project_id=project_id
        )
    )
    return result.id


async def add_tasks_to_repository(
    count: int,
    project_id: UUID,
    status: TaskStatus,
    repository: InMemoryTaskRepository,
) -> None:
    for index in range(count):
        task = Task(
            id=TEST_ID_GENERATOR.new_id(),
            title=f"Test Task {index}",
            description=f"Test Description {index}",
            project_id=project_id,
            status=status,
            created_at=TEST_CLOCK.now(),
        )
        await repository.add(task=task)


async def add_projects_to_repository(
    count: int,
    repository: InMemoryProjectRepository,
) -> None:
    for index in range(count):
        project = Project(
            id=TEST_ID_GENERATOR.new_id(),
            name=f"Test Project {index}",
            description=f"Test Description {index}",
            created_at=TEST_CLOCK.now(),
        )

        await repository.add(project=project)
