from typing import Protocol
from uuid import UUID


class IdGeneratorPort(Protocol):
    def new_id(self) -> UUID:
        pass
