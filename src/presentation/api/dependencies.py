from dataclasses import dataclass
from typing import Annotated
from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.application.use_cases.list_tasks import ListTaskUseCase
from src.application.use_cases.create_task import CreateTaskUseCase
from src.application.use_cases.get_task_by_id import GetTaskByIdUseCase
from src.application.use_cases.update_task import UpdateTaskUseCase
from src.application.use_cases.delete_task import DeleteTaskUseCase
from src.infrastructure.db.repositories.sqlalchemy_task_repository import (
    SqlAlchemyTaskRepository,
)


@dataclass
class ApplicationDependencies:
    create_task: CreateTaskUseCase
    get_task_by_id: GetTaskByIdUseCase
    list_tasks: ListTaskUseCase
    update_task: UpdateTaskUseCase
    delete_task: DeleteTaskUseCase


async def get_session(request: Request) -> AsyncSession:
    async with request.app.state.session_factory() as session:
        yield session


def get_application_dependencies(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ApplicationDependencies:
    repository = SqlAlchemyTaskRepository(session)
    return ApplicationDependencies(
        create_task=CreateTaskUseCase(repository),
        get_task_by_id=GetTaskByIdUseCase(repository),
        list_tasks=ListTaskUseCase(repository),
        update_task=UpdateTaskUseCase(repository),
        delete_task=DeleteTaskUseCase(repository),
    )
