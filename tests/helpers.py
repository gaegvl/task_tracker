from datetime import datetime
from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from src.application.use_cases.create_project import (
    CreateProjectCommand,
    CreateProjectUseCase,
)
from src.application.use_cases.create_task import CreateTaskCommand, CreateTaskUseCase
from src.domain.entities.task import Task, TaskStatus
from src.domain.entities.project import Project
from src.infrastructure.db.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)
from src.infrastructure.db.repositories.in_memory_task_repository import (
    InMemoryTaskRepository,
)


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
    use_case = CreateProjectUseCase(project_repository=repository)
    result = await use_case.execute(
        command=CreateProjectCommand(name=name, description=description)
    )
    return result.id


async def create_task_in_memory(
    task_repository: InMemoryTaskRepository,
    project_repository: InMemoryProjectRepository,
    project_id: UUID,
    title: str = "Test Task",
    description: str = "Test Description",
) -> UUID:
    use_case = CreateTaskUseCase(task_repository, project_repository)
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
            id=uuid4(),
            title=f"Test Task {index}",
            description=f"Test Description {index}",
            project_id=project_id,
            status=status,
            created_at=datetime.now(),
        )
        await repository.add(task=task)


async def add_projects_to_repository(
    count: int,
    repository: InMemoryProjectRepository,
) -> None:
    for index in range(count):
        project = Project(
            id=uuid4(),
            name=f"Test Project {index}",
            description=f"Test Description {index}",
            created_at=datetime.now(),
        )

        await repository.add(project=project)
