from dataclasses import dataclass
from fastapi import Request
from src.application.use_cases.list_tasks import ListTaskUseCase
from src.application.use_cases.create_task import CreateTaskUseCase
from src.application.use_cases.get_task_by_id import GetTaskByIdUseCase


@dataclass
class ApplicationDependencies:
    create_task: CreateTaskUseCase
    get_task_by_id: GetTaskByIdUseCase
    list_tasks: ListTaskUseCase


def get_application_dependencies(request: Request) -> ApplicationDependencies:
    repository = request.app.state.task_repository
    return ApplicationDependencies(
        create_task=CreateTaskUseCase(repository),
        get_task_by_id=GetTaskByIdUseCase(repository),
        list_tasks=ListTaskUseCase(repository),
    )
