# user_router.py

from fastapi import APIRouter, Depends
from starlette import status

from app.api.dependencies.security_dependencies import get_current_user
from app.api.dependencies.service_dependency import get_user_service
from app.api.schemas.user_schema import UserBaseResponse, UserResponse
from app.common.enums import Role
from app.common.exceptions import BusinessException
from app.models import DbUser
from app.services.user_service import UserService

router = APIRouter(
    prefix="",
    tags=["Users"],
)


@router.get("/", response_model=list[UserResponse])
def get_all_users(
    service: UserService = Depends(get_user_service),
    # current_user: DbUser = Depends(get_current_user),
):
    # if current_user.role == Role.ADMIN:
    #     return service.get_all_users()
    # return [current_user]
    return service.get_all_users()


@router.get("/{id}", response_model=UserBaseResponse)
def get_user_info(
    id: int,
    service: UserService = Depends(get_user_service),
    # current_user: DbUser = Depends(get_current_user),
):
    # if current_user.role != Role.ADMIN and current_user.id != id:
    #     raise BusinessException(
    #         message="You do not have permission to access this user",
    #         status_code=status.HTTP_403_FORBIDDEN,
    #     )
    return service.get_user_by_id(user_id=id)


@router.get("/me", response_model=UserBaseResponse)
def get_me(current_user: DbUser = Depends(get_current_user)):
    return current_user
