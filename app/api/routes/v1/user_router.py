# app/api/routes/v1/user_router.py

from fastapi import APIRouter, Depends
from starlette import status

from app.api.dependencies.security_dependencies import get_current_user, require_role
from app.api.dependencies.service_dependency import get_user_service
from app.api.schemas.user_schema import (
    AdminUserResponseSchema,
    UserBaseResponseSchema,
    UserSelfPartialUpdateRequestSchema,
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
    current_user: CurrentUser = Depends(require_role(UserRole.ADMIN)),
):
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
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise BusinessException(
            message="You do not have permission to access this user",
            status_code=status.HTTP_403_FORBIDDEN,
        )
    return service.get_user_by_id(user_id=user_id)


@router.put(
    "/me",
    summary="Update current user profile",
    description="Updates the current user's profile information such as first name and last name.",
    response_model=UserBaseResponseSchema,
)
def update_current_user_profile(
    payload: UserSelfUpdateRequestSchema,
    service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    return service.update_current_user_profile(
        user_id=current_user.id,
        first_name=payload.first_name,
        last_name=payload.last_name,
    )


@router.patch(
    "/me",
    summary="Partially update current user profile",
    description="Updates one or more fields of the current user's profile. Only provided fields will be changed.",
    response_model=UserBaseResponseSchema,
)
def partially_update_current_user_profile(
    payload: UserSelfPartialUpdateRequestSchema,
    service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    return service.partially_update_current_user_profile(
        user_id=current_user.id,
        data=payload.model_dump(exclude_unset=True),
    )
