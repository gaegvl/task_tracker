from datetime import datetime
from uuid import UUID

from src.application.ports.clock import ClockPort
from src.application.ports.id_generator import IdGeneratorPort


class FixedClock(ClockPort):
    def __init__(self, fixed: datetime) -> None:
        self._fixed = fixed

    def now(self) -> datetime:
        return self._fixed


class FixedIdGenerator(IdGeneratorPort):
    def __init__(self, fixed_id: UUID) -> None:
        self._fixed_id = fixed_id

    def new_id(self) -> UUID:
        return self._fixed_id
