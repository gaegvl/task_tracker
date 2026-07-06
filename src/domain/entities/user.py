from dataclasses import dataclass
from enum import StrEnum


class Role(StrEnum):
    USER = "user"
    ADMIN = "admin"


@dataclass(frozen=True)
class CurrentUser:
    role: Role

    def is_admin(self) -> bool:
        return self.role == Role.ADMIN
