from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer

from app.api.dependencies.service_dependency import get_user_service
from app.common.enums import Role
from app.common.exceptions import BusinessException
from app.common.security import decode_token, validate_token_payload
from app.services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/v1/auth/login",
    auto_error=False,
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
):
    if not token:
        raise BusinessException(
            message="Authentication required",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    payload = decode_token(token)
    user_id = validate_token_payload(payload)
    return user_service.get_user_by_id(user_id)


def require_role(role: Role):
    def checker(user=Depends(get_current_user)):
        if user.role != role:
            raise BusinessException(
                message="You do not have permission to perform this action",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return user

    return checker


def require_roles(*roles: Role):
    def checker(user=Depends(get_current_user)):
        if user.role not in roles:
            raise BusinessException(
                message="You do not have permission to perform this action",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return user

    return checker
