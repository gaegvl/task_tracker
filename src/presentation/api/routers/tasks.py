from uuid import UUID
from fastapi import APIRouter, Body, Path, status, Depends, HTTPException
from src.domain.entities.task import TaskStatus
from src.presentation.api.schemas.task import (
    CreateTaskResponse,
    CreateTaskRequest,
    TaskResponse,
)
from src.application.use_cases.create_task import (
    CreateTaskCommand,
    CreateTaskResult,
)
from src.application.use_cases.get_task_by_id import GetTaskByIdCommand
from src.presentation.api.dependencies import (
    ApplicationDependencies,
    get_application_dependencies,
)
from src.domain.exceptions import DomainError, InvalidTaskTitleError, TaskNotFoundError
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
