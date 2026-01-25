# user_router.py

from fastapi import APIRouter, Depends

from app.api.dependencies.service_dependency import get_user_service
from app.api.schemas.user_schema import UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="", tags=["Authentication"])


@router.get("/", response_model=list[UserResponse])
def get_all_users(service: UserService = Depends(get_user_service)):
    return service.get_all_users()


@router.get("/{id}", response_model=UserResponse)
def get_userinfo(id: int, service: UserService = Depends(get_user_service)):
    return service.get_user_by_id(user_id=id)
