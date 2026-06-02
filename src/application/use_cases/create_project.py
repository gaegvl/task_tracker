from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4
from src.domain.entities.project import Project
from src.application.ports.project_repository import ProjectRepositoryPort


@dataclass(frozen=True)
class CreateProjectCommand:
    name: str
    description: str | None


@dataclass(frozen=True)
class CreateProjectResult:
    id: UUID
    name: str
    description: str | None
    created_at: datetime

    @classmethod
    def from_entity(cls, project: Project) -> "CreateProjectResult":
        return cls(
            id=project.id,
            name=project.name,
            description=project.description,
            created_at=project.created_at,
        )


class CreateProjectUseCase:
    def __init__(self, project_repository: ProjectRepositoryPort) -> None:
        self.project_repository = project_repository

    async def execute(self, command: CreateProjectCommand) -> CreateProjectResult:
        project = Project(
            id=uuid4(),
            name=command.name,
            description=command.description,
            created_at=datetime.now(),
        )
        await self.project_repository.add(project=project)
        return CreateProjectResult(
            id=project.id,
            name=project.name,
            description=project.description,
            created_at=project.created_at,
        )
