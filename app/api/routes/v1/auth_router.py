from fastapi import APIRouter, Depends, HTTPException, status

from app.common.exceptions import (
    UserAlreadyExists,
    InvalidPassword,
    InvalidCredentials
)
from app.services.user_service import UserService
from app.api.dependencies.service_dependency import get_user_service
from app.api.schemas.user_schema import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
)



router = APIRouter(prefix="", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
        data: UserRegisterRequest,
        service: UserService = Depends(get_user_service),
):
    try:
        service.register(
            email=str(data.username),
            password=data.password
        )
        return {"message": "User registered successfully"}
    except UserAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )
    except InvalidPassword as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password does not meet security requirements"
        )


@router.post("/login", response_model=TokenResponse)
def login(
        data: UserLoginRequest,
        service: UserService = Depends(get_user_service),
):
    try:

        token = service.login(email=str(data.username), password=data.password)
        return TokenResponse(access_token=token)
    except InvalidCredentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
