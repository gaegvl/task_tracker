from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status

from src.application.use_cases.list_task_status_history import (
    ListTaskStatusHistoryCommand,
)
from src.domain.exceptions import DomainError, TaskNotFoundError
from src.presentation.api.dependencies import (
    ApplicationDependencies,
    get_application_dependencies,
)
from src.presentation.api.schemas.task_status_history import (
    ListTaskStatusHistoryParams,
    TaskStatusChangeResponse,
)

router = APIRouter(prefix="/tasks", tags=["task status history"])


@router.get("/{task_id}/status-history", response_model=list[TaskStatusChangeResponse])
async def list_task_status_history(
    task_id: Annotated[UUID, Path()],
    params: Annotated[ListTaskStatusHistoryParams, Depends()],
    deps: Annotated[ApplicationDependencies, Depends(get_application_dependencies)],
) -> list[TaskStatusChangeResponse]:
    try:
        changes_command = ListTaskStatusHistoryCommand(
            task_id=task_id, limit=params.limit, offset=params.offset
        )
        changes = await deps.list_task_status_history.execute(command=changes_command)
    except TaskNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    return [
        TaskStatusChangeResponse(
            id=change.id,
            task_id=change.task_id,
            from_status=change.from_status,
            to_state=change.to_state,
            changed_at=change.changed_at,
        )
        for change in changes
    ]
