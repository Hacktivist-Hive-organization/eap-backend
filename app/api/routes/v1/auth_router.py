# auth_router.py

from fastapi import APIRouter, Depends, status

from app.api.dependencies.service_dependency import get_auth_service
from app.api.schemas.user_schema import (
    ForgotPasswordRequestSchema,
    ResetPasswordRequestSchema,
    TokenResponseSchema,
    UserLoginRequestSchema,
    UserRegisterRequestSchema,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="", tags=["Authentication"])


@router.post(
    "/register",
    response_model=TokenResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: UserRegisterRequestSchema,
    service: AuthService = Depends(get_auth_service),
):
    token, user = service.register(
        email=str(data.email),
        password=data.password,
        first_name=data.first_name,
        last_name=data.last_name,
    )
    return TokenResponseSchema(access_token=token, user=user)


@router.post("/login", response_model=TokenResponseSchema)
def login(
    data: UserLoginRequestSchema,
    service: AuthService = Depends(get_auth_service),
):
    token, user = service.login(
        email=str(data.email),
        password=data.password,
    )
    return TokenResponseSchema(access_token=token, user=user)


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(
    data: ForgotPasswordRequestSchema,
    service: AuthService = Depends(get_auth_service),
):
    await service.forgot_password(email=data.email)
    return {"message": "If the email exists, a reset link has been sent."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(
    data: ResetPasswordRequestSchema,
    service: AuthService = Depends(get_auth_service),
):
    service.reset_password(
        token=data.token,
        new_password=data.new_password,
    )
    return {"message": "Password successfully reset."}
