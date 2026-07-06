from src.application.ports.auth import AuthPort
from src.domain.entities.user import CurrentUser, Role
from src.domain.exceptions import AuthenticationError


class ApiKeyAuthenticator(AuthPort):
    def __init__(self, user_api_key: str, admin_api_key: str) -> None:
        self._keys: dict[str, Role] = {
            user_api_key: Role.USER,
            admin_api_key: Role.ADMIN,
        }

    def authenticate(self, api_key: str) -> CurrentUser:
        role = self._keys.get(api_key)
        if role is None:
            raise AuthenticationError()
        return CurrentUser(role=role)
