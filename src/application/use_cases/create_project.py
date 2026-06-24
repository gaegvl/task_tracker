from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from src.application.ports.clock import ClockPort
from src.application.ports.id_generator import IdGeneratorPort
from src.application.ports.project_repository import ProjectRepositoryPort
from src.domain.entities.project import Project


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
    def from_entity(cls, project: Project) -> CreateProjectResult:
        return cls(
            id=project.id,
            name=project.name,
            description=project.description,
            created_at=project.created_at,
        )


class CreateProjectUseCase:
    def __init__(
        self,
        project_repository: ProjectRepositoryPort,
        clock: ClockPort,
        id_generator: IdGeneratorPort,
    ) -> None:
        self.project_repository = project_repository
        self.clock = clock
        self.id_generator = id_generator

    async def execute(self, command: CreateProjectCommand) -> CreateProjectResult:
        project = Project(
            id=self.id_generator.new_id(),
            name=command.name,
            description=command.description,
            created_at=self.clock.now(),
        )
        await self.project_repository.add(project=project)
        return CreateProjectResult(
            id=project.id,
            name=project.name,
            description=project.description,
            created_at=project.created_at,
        )
