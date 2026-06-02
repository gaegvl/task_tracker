from fastapi import APIRouter, Body, HTTPException, status, Depends, Path
from typing import Annotated
from src.domain.exceptions import (
    DomainError,
    InvalidProjectNameError,
    ProjectHasTasksError,
    ProjectNotFoundError,
)
from src.application.use_cases.delete_project import DeleteProjectCommand
from src.application.use_cases.list_projects import ListProjectsCommand
from src.application.use_cases.get_project_by_id import GetProjectByIdCommand
from src.application.use_cases.create_project import CreateProjectCommand
from src.application.use_cases.update_project import UpdateProjectCommand
from uuid import UUID
from src.presentation.api.dependencies import (
    ApplicationDependencies,
    get_application_dependencies,
)
from src.presentation.api.schemas.project import (
    CreateProjectResponse,
    CreateProjectRequest,
    ListProjectsParams,
    UpdateProjectRequest,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post(
    "/", response_model=CreateProjectResponse, status_code=status.HTTP_201_CREATED
)
async def crete_project(
    project: Annotated[CreateProjectRequest, Body()],
    deps: Annotated[ApplicationDependencies, Depends(get_application_dependencies)],
) -> CreateProjectResponse:
    try:
        result = await deps.create_project.execute(
            command=CreateProjectCommand(
                name=project.name, description=project.description
            )
        )
        return CreateProjectResponse(
            id=result.id,
            name=result.name,
            description=result.description,
            created_at=result.created_at,
        )
    except InvalidProjectNameError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid project name"
        )
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get(
    "/", response_model=list[CreateProjectResponse], status_code=status.HTTP_200_OK
)
async def list_projects(
    params: Annotated[ListProjectsParams, Depends()],
    deps: Annotated[ApplicationDependencies, Depends(get_application_dependencies)],
) -> list[CreateProjectResponse]:
    result = await deps.list_projects.execute(
        command=ListProjectsCommand(limit=params.limit, offset=params.offset)
    )
    return [
        CreateProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            created_at=project.created_at,
        )
        for project in result
    ]


@router.get(
    "/{project_id}",
    response_model=CreateProjectResponse,
    status_code=status.HTTP_200_OK,
)
async def get_project_by_id(
    project_id: Annotated[UUID, Path()],
    deps: Annotated[ApplicationDependencies, Depends(get_application_dependencies)],
) -> CreateProjectResponse:
    try:
        result = await deps.get_project_by_id.execute(
            command=GetProjectByIdCommand(id=project_id)
        )
        return CreateProjectResponse(
            id=result.id,
            name=result.name,
            description=result.description,
            created_at=result.created_at,
        )
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.patch(
    "/{project_id}",
    response_model=CreateProjectResponse,
    status_code=status.HTTP_200_OK,
)
async def update_project(
    project_id: Annotated[UUID, Path()],
    project: Annotated[UpdateProjectRequest, Body()],
    deps: Annotated[ApplicationDependencies, Depends(get_application_dependencies)],
) -> CreateProjectResponse:
    try:
        await deps.get_project_by_id.execute(
            command=GetProjectByIdCommand(id=project_id)
        )

        result = await deps.update_project.execute(
            command=UpdateProjectCommand(
                id=project_id, name=project.name, description=project.description
            )
        )
        return CreateProjectResponse(
            id=result.id,
            name=result.name,
            description=result.description,
            created_at=result.created_at,
        )
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: Annotated[UUID, Path()],
    deps: Annotated[ApplicationDependencies, Depends(get_application_dependencies)],
) -> None:
    try:
        await deps.get_project_by_id.execute(
            command=GetProjectByIdCommand(id=project_id)
        )
        await deps.delete_project.execute(command=DeleteProjectCommand(id=project_id))
        return
    except ProjectHasTasksError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Project has tasks"
        )
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    except DomainError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
