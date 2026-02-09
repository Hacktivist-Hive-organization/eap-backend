# app/api/dependencies/security_dependencies.py

from fastapi import Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.dependencies.service_dependency import get_user_service
from app.common.enums import UserRole
from app.common.exceptions import BusinessException
from app.common.security import validate_token_payload, verify_token
from app.models.security_models import CurrentUser
from app.services.user_service import UserService

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    user_service: UserService = Depends(get_user_service),
) -> CurrentUser:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise BusinessException(
            message="Authentication required",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    token = credentials.credentials
    payload = verify_token(token)
    user_id = validate_token_payload(payload)

    user = user_service.get_user_by_id(user_id)
    if not user:
        raise BusinessException(
            message="User not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return CurrentUser(
        id=user.id,
        role=user.role,
    )


def require_role(role: UserRole):
    def checker(user: CurrentUser = Depends(get_current_user)):
        if user.role != role:
            raise BusinessException(
                message="You do not have permission to perform this action",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return user

    return checker


def require_roles(*roles: UserRole):
    def checker(user: CurrentUser = Depends(get_current_user)):
        if user.role not in roles:
            raise BusinessException(
                message="You do not have permission to perform this action",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return user

    return checker
