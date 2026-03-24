# app/api/routes/v1/auth_router.py

from fastapi import APIRouter, BackgroundTasks, Depends, status

from app.api.dependencies.service_dependency import get_auth_service
from app.api.schemas.user_schema import (
    ForgotPasswordRequestSchema,
    ResendVerificationEmailRequestSchema,
    ResetPasswordRequestSchema,
    TokenResponseSchema,
    UserLoginRequestSchema,
    UserRegisterRequestSchema,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="", tags=["Authentication"])


@router.post(
    "/register",
    summary="Register user account",
    description="Creates a new user account and returns an access token for authenticated requests.",
    response_model=TokenResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: UserRegisterRequestSchema,
    background_tasks: BackgroundTasks,
    service: AuthService = Depends(get_auth_service),
):
    token, user = service.register(
        email=str(data.email),
        password=data.password,
        first_name=data.first_name,
        last_name=data.last_name,
        background_tasks=background_tasks,
    )
    return TokenResponseSchema(access_token=token, user=user)


@router.post(
    "/login",
    summary="Authenticate user",
    description="Authenticates a user using email and password and returns an access token.",
    response_model=TokenResponseSchema,
)
def login(
    data: UserLoginRequestSchema,
    service: AuthService = Depends(get_auth_service),
):
    token, user = service.login(
        email=str(data.email),
        password=data.password,
    )
    return TokenResponseSchema(access_token=token, user=user)


@router.post(
    "/forgot-password",
    summary="Request password reset",
    description="Starts the password reset process. If the provided email exists, a password reset token will be sent to that address.",
    status_code=status.HTTP_200_OK,
)
def forgot_password(
    data: ForgotPasswordRequestSchema,
    background_tasks: BackgroundTasks,
    service: AuthService = Depends(get_auth_service),
):
    service.forgot_password(
        email=data.email,
        background_tasks=background_tasks,
    )
    return {"message": "If the email exists, a reset link has been sent."}


@router.post(
    "/reset-password",
    summary="Reset password",
    description="Resets the user password using the reset token received by email and sets a new password.",
    status_code=status.HTTP_200_OK,
)
def reset_password(
    data: ResetPasswordRequestSchema,
    service: AuthService = Depends(get_auth_service),
):
    service.reset_password(
        token=data.token,
        new_password=data.new_password,
    )
    return {"message": "Password successfully reset."}


@router.get(
    "/verify-email",
    summary="Verify user email",
    description="Verifies a user's email address using the verification token sent to their email.",
    status_code=status.HTTP_200_OK,
)
def verify_email(
    token: str,
    background_tasks: BackgroundTasks,
    service: AuthService = Depends(get_auth_service),
):
    service.verify_email(token, background_tasks)
    return {"message": "Email successfully verified."}


@router.post(
    "/resend-verification-email",
    summary="Resend verification email",
    description="Resends the email verification link if the account exists and the email is not yet verified.",
    status_code=status.HTTP_200_OK,
)
def resend_verification_email(
    data: ResendVerificationEmailRequestSchema,
    background_tasks: BackgroundTasks,
    service: AuthService = Depends(get_auth_service),
):
    sent = service.resend_verification_email(
        email=data.email,
        background_tasks=background_tasks,
    )

    if sent:
        message = "A verification link has been sent to your email."
    else:
        message = "Email verification is not required or email does not exist."

    return {"message": message}
