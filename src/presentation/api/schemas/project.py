from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class CreateProjectRequest(BaseModel):
    name: str
    description: str | None = None


class CreateProjectResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    created_at: datetime


class UpdateProjectRequest(BaseModel):
    name: str | None = None
    description: str | None = None


class UpdateProjectResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    created_at: datetime


class ListProjectsParams(BaseModel):
    limit: int = Field(ge=1, le=100, default=10)
    offset: int = Field(ge=0, default=0)
