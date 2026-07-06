from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.application.ports.auth import AuthPort
from src.domain.entities.user import CurrentUser
from src.domain.exceptions import AuthenticationError
from src.infrastructure.auth.api_key_authenticator import ApiKeyAuthenticator
from src.infrastructure.config import get_settings

security = HTTPBearer(auto_error=False)


def get_auth_port() -> AuthPort:
    settings = get_settings()
    return ApiKeyAuthenticator(settings.user_api_key, settings.admin_api_key)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    auth: Annotated[AuthPort, Depends(get_auth_port)],
) -> CurrentUser:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    try:
        return auth.authenticate(credentials.credentials)
    except AuthenticationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )


def require_admin(
    user: Annotated[CurrentUser, Depends(get_current_user)],
) -> CurrentUser:
    if not user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return user


def get_optional_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    auth: Annotated[AuthPort, Depends(get_auth_port)],
) -> CurrentUser | None:
    if credentials is None:
        return None
    try:
        return auth.authenticate(credentials.credentials)
    except AuthenticationError:
        raise HTTPException(status_code=401, detail="Invalid API key")
