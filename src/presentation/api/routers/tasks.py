from uuid import UUID
from fastapi import APIRouter, Body, Path, status, Depends, HTTPException
from src.application.use_cases.purge_task import PurgeTaskCommand
from src.application.use_cases.restore_task import RestoreTaskCommand
from src.application.use_cases.delete_task import DeleteTaskCommand
from src.application.use_cases.update_task import UpdateTaskCommand
from src.domain.entities.task import TaskStatus
from src.presentation.api.schemas.task import (
    CreateTaskResponse,
    CreateTaskRequest,
    TaskResponse,
    ListTasksParams,
    UpdateTaskRequest,
)
from src.application.use_cases.create_task import (
    CreateTaskCommand,
    CreateTaskResult,
)
from src.application.use_cases.get_task_by_id import GetTaskByIdCommand
from src.application.use_cases.list_tasks import ListTasksCommand
from src.presentation.api.dependencies import (
    ApplicationDependencies,
    get_application_dependencies,
)
from src.domain.exceptions import (
    DomainError,
    InvalidTaskTitleError,
    ProjectNotFoundError,
    TaskNotFoundError,
    InvalidTaskStatusTransitionError,
)
from typing import Annotated

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post(
    "/", response_model=CreateTaskResponse, status_code=status.HTTP_201_CREATED
)
async def create_task(
    task: Annotated[CreateTaskRequest, Body],
    deps: Annotated[ApplicationDependencies, Depends(get_application_dependencies)],
) -> CreateTaskResponse:
    try:
        result: CreateTaskResult = await deps.create_task.execute(
            command=CreateTaskCommand(**task.model_dump())
        )
    except InvalidTaskTitleError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid task title"
        )
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    return CreateTaskResponse(
        id=result.id,
        title=result.title,
        status=TaskStatus(result.status),
        created_at=result.created_at,
    )


@router.get("/", response_model=list[TaskResponse], status_code=status.HTTP_200_OK)
async def get_list_tasks(
    params: Annotated[ListTasksParams, Depends()],
    deps: Annotated[ApplicationDependencies, Depends(get_application_dependencies)],
) -> list[TaskResponse]:
    result = await deps.list_tasks.execute(
        command=ListTasksCommand(
            project_id=params.project_id,
            status=params.status,
            limit=params.limit,
            offset=params.offset,
        )
    )
    return [
        TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            project_id=task.project_id,
            status=TaskStatus(task.status),
            created_at=task.created_at,
        )
        for task in result.items
    ]


@router.get("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
async def get_task_by_id(
    task_id: Annotated[UUID, Path()],
    deps: Annotated[ApplicationDependencies, Depends(get_application_dependencies)],
) -> TaskResponse:
    try:
        result = await deps.get_task_by_id.execute(
            command=GetTaskByIdCommand(id=task_id)
        )
    except TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    return TaskResponse(
        id=result.id,
        title=result.title,
        description=result.description,
        project_id=result.project_id,
        status=TaskStatus(result.status),
        created_at=result.created_at,
    )


@router.patch("/{task_id}", response_model=TaskResponse, status_code=status.HTTP_200_OK)
async def update_task(
    task_id: Annotated[UUID, Path()],
    command: Annotated[UpdateTaskRequest, Body()],
    deps: Annotated[ApplicationDependencies, Depends(get_application_dependencies)],
) -> TaskResponse:
    try:
        updated_task = await deps.update_task.execute(
            command=UpdateTaskCommand(
                task_id=task_id,
                status=command.status,
                title=command.title,
                description=command.description,
                project_id=command.project_id,
            )
        )
        return TaskResponse(
            id=updated_task.id,
            title=updated_task.title,
            description=updated_task.description,
            project_id=updated_task.project_id,
            status=TaskStatus(updated_task.status),
            created_at=updated_task.created_at,
        )
    except InvalidTaskStatusTransitionError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Invalid task status transition",
        )
    except TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: Annotated[UUID, Path()],
    deps: Annotated[ApplicationDependencies, Depends(get_application_dependencies)],
) -> None:
    try:
        command = DeleteTaskCommand(task_id=task_id)
        await deps.delete_task.execute(command=command)
    except TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post(
    "/{task_id}/restore", response_model=TaskResponse, status_code=status.HTTP_200_OK
)
async def restore_task(
    task_id: Annotated[UUID, Path()],
    deps: Annotated[ApplicationDependencies, Depends(get_application_dependencies)],
) -> TaskResponse:
    command = RestoreTaskCommand(task_id=task_id)
    try:
        result = await deps.restore_task.execute(command=command)
    except TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    return TaskResponse(
        id=result.id,
        title=result.title,
        description=result.description,
        project_id=result.project_id,
        status=TaskStatus(result.status),
        created_at=result.created_at,
    )


@router.delete("/{task_id}/purge", status_code=status.HTTP_204_NO_CONTENT)
async def purge_task(
    task_id: Annotated[UUID, Path()],
    deps: Annotated[ApplicationDependencies, Depends(get_application_dependencies)],
) -> None:
    try:
        command = PurgeTaskCommand(task_id=task_id)
        await deps.purge_task.execute(command=command)
    except TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
