from uuid import UUID, uuid4

from src.application.ports.id_generator import IdGeneratorPort


class SystemIdGenerator(IdGeneratorPort):
    def new_id(self) -> UUID:
        return uuid4()
