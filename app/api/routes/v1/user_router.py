# app/api/routes/v1/user_router.py

from fastapi import APIRouter, Depends
from starlette import status

from app.api.dependencies.security_dependencies import get_current_user
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


@router.get("/", response_model=list[AdminUserResponseSchema])
def get_all_users(
    service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    if current_user.role == UserRole.ADMIN:
        return service.get_all_users()
    raise BusinessException(
        message="You do not have permission to access this user",
        status_code=status.HTTP_403_FORBIDDEN,
    )


@router.get("/me", response_model=UserBaseResponseSchema)
def get_me(
    service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    return service.get_user_by_id(current_user.id)


@router.get("/{id}", response_model=AdminUserResponseSchema)
def get_user_info(
    id: int,
    service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    if current_user.role != UserRole.ADMIN and current_user.id != id:
        raise BusinessException(
            message="You do not have permission to access this user",
            status_code=status.HTTP_403_FORBIDDEN,
        )
    return service.get_user_by_id(user_id=id)


@router.put("/me", response_model=UserBaseResponseSchema)
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


@router.patch("/me", response_model=UserBaseResponseSchema)
def partially_update_current_user_profile(
    payload: UserSelfPartialUpdateRequestSchema,
    service: UserService = Depends(get_user_service),
    current_user: CurrentUser = Depends(get_current_user),
):
    return service.partially_update_current_user_profile(
        user_id=current_user.id,
        data=payload.model_dump(exclude_unset=True),
    )
