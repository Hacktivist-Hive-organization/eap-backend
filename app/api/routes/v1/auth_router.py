# auth_router.py

from fastapi import APIRouter, Depends, status

from app.api.dependencies.service_dependency import get_user_service
from app.api.schemas.user_schema import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
)
from app.services.user_service import UserService

router = APIRouter(prefix="", tags=["Authentication"])


@router.post(
    "/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
def register(
    data: UserRegisterRequest, service: UserService = Depends(get_user_service)
):
    token = service.register(
        email=str(data.email),
        password=data.password,
        first_name=data.first_name,
        last_name=data.last_name,
    )
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(data: UserLoginRequest, service: UserService = Depends(get_user_service)):
    token = service.login(email=str(data.email), password=data.password)
    return TokenResponse(access_token=token)
