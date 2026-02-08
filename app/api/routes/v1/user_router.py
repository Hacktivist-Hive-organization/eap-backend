# app/api/routes/v1/user_router.py

from fastapi import APIRouter, Depends
from starlette import status

from app.api.dependencies.security_dependencies import get_current_user
from app.api.dependencies.service_dependency import get_user_service
from app.api.schemas.user_schema import (
    UserBaseResponse,
    UserResponse,
    UserSelfPartialUpdateRequest,
    UserSelfUpdateRequest,
)
from app.common.enums import UserRole
from app.common.exceptions import BusinessException
from app.models.db_user import DbUser
from app.services.user_service import UserService

router = APIRouter(
    prefix="",
    tags=["Users"],
)


@router.get("/", response_model=list[UserResponse])
def get_all_users(
    service: UserService = Depends(get_user_service),
    current_user: DbUser = Depends(get_current_user),
):
    if current_user.role == UserRole.ADMIN:
        return service.get_all_users()
    return [current_user]


@router.get("/me", response_model=UserBaseResponse)
def get_me(
    current_user: DbUser = Depends(get_current_user),
):
    return current_user


@router.get("/{id}", response_model=UserBaseResponse)
def get_user_info(
    id: int,
    service: UserService = Depends(get_user_service),
    current_user: DbUser = Depends(get_current_user),
):
    if current_user.role != UserRole.ADMIN and current_user.id != id:
        raise BusinessException(
            message="You do not have permission to access this user",
            status_code=status.HTTP_403_FORBIDDEN,
        )
    return service.get_user_by_id(user_id=id)


@router.put("/me", response_model=UserBaseResponse)
def update_current_user_profile(
    payload: UserSelfUpdateRequest,
    service: UserService = Depends(get_user_service),
    current_user: DbUser = Depends(get_current_user),
):
    user_model = service.get_user_by_id(current_user.id)
    return service.update_current_user_profile(
        current_user=user_model,
        first_name=payload.first_name,
        last_name=payload.last_name,
    )


@router.patch("/me", response_model=UserBaseResponse)
def partially_update_current_user_profile(
    payload: UserSelfPartialUpdateRequest,
    service: UserService = Depends(get_user_service),
    current_user: DbUser = Depends(get_current_user),
):
    user_model = service.get_user_by_id(current_user.id)
    return service.partially_update_current_user_profile(
        current_user=user_model,
        data=payload.model_dump(exclude_unset=True),
    )
