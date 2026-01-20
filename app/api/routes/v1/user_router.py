from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.service_dependency import get_user_service
from app.api.schemas.user_schema import UserResponse
from app.common.exceptions import UserNotFound
from app.services.user_service import UserService

router = APIRouter(prefix="", tags=["Authentication"])


@router.get("/", response_model=list[UserResponse])
def get_all_users(service: UserService = Depends(get_user_service)):
    data = service.get_all_users()
    return data


@router.get("/{id}", response_model=UserResponse)
def get_userinfo(id: int, service: UserService = Depends(get_user_service)):
    try:
        data = service.get_user_by_id(user_id=id)
        return data
    except UserNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
