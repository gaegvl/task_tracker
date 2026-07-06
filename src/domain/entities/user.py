from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class Role(StrEnum):
    USER = "user"
    ADMIN = "admin"


@dataclass(frozen=True)
class CurrentUser:
    id: UUID
    role: Role

    def is_admin(self) -> bool:
        return self.role == Role.ADMIN


@dataclass(frozen=True)
class User:
    id: UUID
    display_name: str
    role: Role
