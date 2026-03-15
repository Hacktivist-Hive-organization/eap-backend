# app/api/routes/v1/user_router.py

from fastapi import APIRouter, Depends
from starlette import status

from app.api.dependencies.security_dependencies import get_current_user, require_role
from app.api.dependencies.service_dependency import get_user_service
from app.api.schemas.user_schema import (
    AdminUserResponseSchema,
    UserAdminUpdateRequestSchema,
    UserBaseResponseSchema,
    UserSelfUpdateRequestSchema,
)
from app.common.enums import UserRole
from app.common.exceptions import BusinessException
from app.common.security_models import CurrentUser
from app.services.user_service import UserService

router = APIRouter(
    prefix="",
    tags=["Users"],
)


@router.get(
    "/",
    summary="Get all users",
    description="Returns a list of all users. Accessible only to administrators.",
    response_model=list[AdminUserResponseSchema],
)
def get_all_users(
    service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    if current_user.role != UserRole.ADMIN:
        raise BusinessException(
            message="You do not have permission to access all users",
            status_code=status.HTTP_403_FORBIDDEN,
        )
    return service.get_all_users()


@router.get(
    "/me",
    summary="Get current user profile",
    description="Returns the profile information of the currently authenticated user.",
    response_model=UserBaseResponseSchema,
)
def get_me(
    service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    return service.get_user_by_id(current_user.id)


@router.get(
    "/{user_id}",
    summary="Get user by ID",
    description="Returns user information by ID. Accessible to administrators or the user who owns the account.",
    response_model=AdminUserResponseSchema,
)
def get_user_info(
    user_id: int,
    service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    return service.get_user_by_id_for_current_user(
        user_id=user_id,
        current_user=current_user,
    )


@router.patch(
    "/me",
    summary="Self update user profile",
    description="Updates one or more fields of the current user's profile. Only self fields are allowed.",
    response_model=UserBaseResponseSchema,
)
def update_current_user_profile(
    payload: UserSelfUpdateRequestSchema,
    service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    return service.current_user_update_profile(
        current_user=current_user,
        data=payload.model_dump(exclude_unset=True),
    )


@router.patch(
    "/{user_id}",
    summary="Admin update user profile",
    description="Allows an administrator to update fields of any user, including role and is_active.",
    response_model=AdminUserResponseSchema,
)
def admin_update_user_profile(
    user_id: int,
    payload: UserAdminUpdateRequestSchema,
    service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    if current_user.role != UserRole.ADMIN:
        raise BusinessException(
            message="You do not have permission to update other users",
            status_code=status.HTTP_403_FORBIDDEN,
        )
    return service.admin_update_profile(
        user_id=user_id,
        data=payload.model_dump(exclude_unset=True),
        current_user=current_user,
    )
