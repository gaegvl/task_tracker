from typing import Protocol

from src.domain.entities.user import CurrentUser


class AuthPort(Protocol):
    def authenticate(self, api_key: str) -> CurrentUser:
        pass
