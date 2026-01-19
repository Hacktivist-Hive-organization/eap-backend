from fastapi import APIRouter, Depends, HTTPException, status
from app.services.user_service import UserService
from app.api.dependencies.service_dependency import get_user_service
from app.api.schemas.user_schema import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
        data: UserRegisterRequest,
        service: UserService = Depends(get_user_service),
):
    try:
        service.register(email=data.username, password=data.password)
        return {"message": "User registered successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(
        data: UserLoginRequest,
        service: UserService = Depends(get_user_service),
):
    try:
        token = service.login(email=data.username, password=data.password)
        return TokenResponse(access_token=token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
