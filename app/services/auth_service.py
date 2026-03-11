# app/services/auth_service.py

from datetime import datetime, timezone

from fastapi import BackgroundTasks, status

from app.common.exceptions import BusinessException
from app.common.security import (
    hash_password,
    verify_password,
    verify_token,
)
from app.common.utils import (
    create_jwt_token,
    is_email_valid,
    is_password_strong,
    is_required_fields_filled,
    normalize_email,
)
from app.core.config import settings
from app.models.db_user import DbUser
from app.repositories.user_repository import UserRepository
from app.services.email_service import EmailService


class AuthService:
    def __init__(self, repo: UserRepository, email_service: EmailService):
        self.repo = repo
        self.email_service = email_service

    def register(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        background_tasks: BackgroundTasks,
    ) -> tuple[str, DbUser]:

        normalized_email = normalize_email(email)

        checks = [
            {
                "func": lambda: is_required_fields_filled(
                    email=normalized_email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                ),
                "message": "All required fields must be filled",
                "status": status.HTTP_422_UNPROCESSABLE_CONTENT,
            },
            {
                "func": lambda: is_email_valid(normalized_email),
                "message": "Invalid email or password",
                "status": status.HTTP_422_UNPROCESSABLE_CONTENT,
            },
            {
                "func": lambda: not self.repo.get_by_email(normalized_email),
                "message": "User already exists",
                "status": status.HTTP_409_CONFLICT,
            },
            {
                "func": lambda: is_password_strong(password),
                "message": "Password is too weak",
                "status": status.HTTP_422_UNPROCESSABLE_CONTENT,
            },
        ]

        for check in checks:
            if not check["func"]():
                raise BusinessException(
                    message=check["message"],
                    status_code=check["status"],
                )

        hashed_password = hash_password(password)

        is_active = not settings.EMAIL_VERIFICATION_REQUIRED
        is_email_verified = not settings.EMAIL_VERIFICATION_REQUIRED

        user = self.repo.create(
            email=normalized_email,
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            is_active=is_active,
            is_email_verified=is_email_verified,
        )

        if settings.EMAIL_VERIFICATION_REQUIRED:
            verification_token = create_jwt_token(user.id, "email_verification")
            self.email_service.send_verification_email(
                user.email, verification_token, background_tasks
            )

        token = create_jwt_token(user.id, "access")

        return token, user

    def login(self, email: str, password: str) -> tuple[str, DbUser]:

        normalized_email = normalize_email(email)

        if not is_email_valid(normalized_email):
            raise BusinessException(
                message="Invalid email or password",
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            )

        user = self.repo.get_by_email(normalized_email)

        if not user or not verify_password(password, user.hashed_password):
            raise BusinessException(
                message="Invalid email or password",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        user.last_login = datetime.now(timezone.utc)
        self.repo.update_user(user)

        token = create_jwt_token(user.id, "access")
        return token, user

    def forgot_password(self, email: str, background_tasks: BackgroundTasks) -> bool:
        normalized_email = normalize_email(email)

        if not is_email_valid(normalized_email):
            raise BusinessException(
                message="Invalid email format",
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            )

        user = self.repo.get_by_email(normalized_email)
        if not user:
            return False

        token = create_jwt_token(user.id, "password_reset")

        self.email_service.send_password_reset_email(
            user.email, token, background_tasks
        )

        return True

    def reset_password(self, token: str, new_password: str) -> None:
        if not is_password_strong(new_password):
            raise BusinessException(
                message="Password is too weak",
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            )

        payload = verify_token(token)

        if payload.get("type") != "password_reset":
            raise BusinessException(
                message="Invalid token type",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        user_id = payload.get("sub")
        if not user_id:
            raise BusinessException(
                message="Invalid token payload",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        user = self.repo.get_user(int(user_id))
        if not user:
            raise BusinessException(
                message="User not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        user.hashed_password = hash_password(new_password)
        self.repo.update_user(user)

    def verify_email(self, token: str, background_tasks: BackgroundTasks) -> None:
        payload = verify_token(token)
        if payload.get("type") != "email_verification":
            raise BusinessException(
                message="Invalid token type",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        user_id = payload.get("sub")
        if not user_id:
            raise BusinessException(
                message="Invalid token payload",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        user = self.repo.get_user(int(user_id))
        if not user:
            raise BusinessException(
                message="User not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        user.is_active = True
        user.is_email_verified = True
        self.repo.update_user(user)

        self.email_service.send_account_verified_email(user.email, background_tasks)

    def resend_verification_email(
        self,
        email: str,
        background_tasks: BackgroundTasks,
    ) -> bool:
        normalized_email = normalize_email(email)

        if not is_email_valid(normalized_email):
            raise BusinessException(
                message="Invalid email format",
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            )

        user = self.repo.get_by_email(normalized_email)
        if not user or user.is_email_verified:
            return False

        verification_token = create_jwt_token(user.id, "email_verification")
        self.email_service.send_verification_email(
            user.email, verification_token, background_tasks
        )

        return True
