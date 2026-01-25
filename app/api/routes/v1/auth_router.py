# auth_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.api.dependencies.service_dependency import get_user_service
from app.api.schemas.user_schema import (
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
)
from app.common.exceptions import InvalidCredentials, InvalidPassword, UserAlreadyExists
from app.services.user_service import UserService

router = APIRouter(prefix="", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    data: UserRegisterRequest,
    service: UserService = Depends(get_user_service),
):
    try:
        service.register(
            email=str(data.email),
            password=data.password,
            first_name=data.first_name,
            last_name=data.last_name,
        )
        return {"message": "User registered successfully"}
    except InvalidPassword:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Password does not meet security requirements",
        )

    except UserAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )

    except IntegrityError:
        service.repo.db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )


@router.post("/login", response_model=TokenResponse)
def login(
    data: UserLoginRequest,
    service: UserService = Depends(get_user_service),
):
    try:

        token = service.login(email=str(data.email), password=data.password)
        return TokenResponse(access_token=token)
    except InvalidCredentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
