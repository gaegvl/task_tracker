from dataclasses import dataclass
from typing import Annotated
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.use_cases.list_task_status_history import (
    ListTaskStatusHistoryUseCase,
)
from src.application.use_cases.list_tasks import ListTaskUseCase
from src.application.use_cases.create_task import CreateTaskUseCase
from src.application.use_cases.get_task_by_id import GetTaskByIdUseCase
from src.application.use_cases.update_task import UpdateTaskUseCase
from src.application.use_cases.delete_task import DeleteTaskUseCase

from src.application.use_cases.create_project import CreateProjectUseCase
from src.application.use_cases.get_project_by_id import GetProjectByIdUseCase
from src.application.use_cases.update_project import UpdateProjectUseCase
from src.application.use_cases.delete_project import DeleteProjectUseCase
from src.application.use_cases.list_projects import ListProjectsUseCase
from src.infrastructure.db.repositories.sqlalchemy_task_repository import (
    SqlAlchemyTaskRepository,
)
from src.infrastructure.db.repositories.sqlalchemy_task_status_history_repository import (
    SqlAlchemyTaskStatusHistoryRepository,
)
from src.infrastructure.db.repositories.sqlalchemy_project_repository import (
    SqlAlchemyProjectRepository,
)
from src.application.use_cases.restore_task import RestoreTaskUseCase
from src.application.use_cases.restore_project import RestoreProjectUseCase
from src.application.use_cases.purge_task import PurgeTaskUseCase
from src.application.use_cases.purge_project import PurgeProjectUseCase


@dataclass
class ApplicationDependencies:
    create_task: CreateTaskUseCase
    get_task_by_id: GetTaskByIdUseCase
    list_tasks: ListTaskUseCase
    update_task: UpdateTaskUseCase
    delete_task: DeleteTaskUseCase
    create_project: CreateProjectUseCase
    get_project_by_id: GetProjectByIdUseCase
    list_projects: ListProjectsUseCase
    update_project: UpdateProjectUseCase
    delete_project: DeleteProjectUseCase
    restore_task: RestoreTaskUseCase
    restore_project: RestoreProjectUseCase
    list_task_status_history: ListTaskStatusHistoryUseCase
    purge_task: PurgeTaskUseCase
    purge_project: PurgeProjectUseCase


async def get_session(request: Request) -> AsyncSession:
    async with request.app.state.session_factory() as session:
        yield session


def get_application_dependencies(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ApplicationDependencies:
    task_repository = SqlAlchemyTaskRepository(session)
    project_repository = SqlAlchemyProjectRepository(session)
    task_status_history_repository = SqlAlchemyTaskStatusHistoryRepository(session)
    return ApplicationDependencies(
        create_task=CreateTaskUseCase(task_repository, project_repository),
        get_task_by_id=GetTaskByIdUseCase(task_repository),
        list_tasks=ListTaskUseCase(task_repository),
        update_task=UpdateTaskUseCase(
            task_repository, project_repository, task_status_history_repository
        ),
        delete_task=DeleteTaskUseCase(task_repository),
        create_project=CreateProjectUseCase(project_repository),
        get_project_by_id=GetProjectByIdUseCase(project_repository),
        list_projects=ListProjectsUseCase(project_repository),
        update_project=UpdateProjectUseCase(project_repository),
        delete_project=DeleteProjectUseCase(project_repository, task_repository),
        restore_task=RestoreTaskUseCase(task_repository, project_repository),
        restore_project=RestoreProjectUseCase(project_repository, task_repository),
        list_task_status_history=ListTaskStatusHistoryUseCase(
            task_status_history_repository, task_repository
        ),
        purge_task=PurgeTaskUseCase(task_repository),
        purge_project=PurgeProjectUseCase(project_repository, task_repository),
    )
