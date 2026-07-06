from src.application.ports.auth import AuthPort
from src.domain.entities.user import CurrentUser, Role
from src.domain.exceptions import AuthenticationError
from src.infrastructure.db.seed_users import ADMIN_USER_ID, USER_USER_ID


class ApiKeyAuthenticator(AuthPort):
    def __init__(self, user_api_key: str, admin_api_key: str) -> None:
        self._keys: dict[str, CurrentUser] = {
            user_api_key: CurrentUser(id=USER_USER_ID, role=Role.USER),
            admin_api_key: CurrentUser(id=ADMIN_USER_ID, role=Role.ADMIN),
        }

    def authenticate(self, api_key: str) -> CurrentUser:
        current_user = self._keys.get(api_key)
        if current_user is None:
            raise AuthenticationError()
        return current_user
