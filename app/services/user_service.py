# user_service.py
from fastapi import status

from app.common.exceptions import BusinessException
from app.common.security import (
    create_access_token,
    hash_password,
    validate_password,
    verify_password,
)
from app.models.db_user import DbUser
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def get_user_by_id(self, user_id: int) -> DbUser | None:
        user = self.repo.get_user(user_id=user_id)
        if not user:
            raise BusinessException(
                message="User not found", status_code=status.HTTP_404_NOT_FOUND
            )
        return user

    def get_all_users(self) -> list[DbUser]:
        return self.repo.get_all_users()

    def register(
        self, email: str, password: str, first_name: str, last_name: str
    ) -> tuple[str, DbUser]:
        normalized_email = email.lower()

        if self.repo.get_by_email(normalized_email):
            raise BusinessException(
                message="User already exists", status_code=status.HTTP_409_CONFLICT
            )

        validate_password(password)
        hashed_password = hash_password(password)

        user = self.repo.create(
            email=normalized_email,
            hashed_password=hashed_password,
            first_name=first_name,
            last_name=last_name,
        )

        token = create_access_token({"sub": str(user.id)})
        return token, user

    def login(self, email: str, password: str) -> tuple[str, DbUser]:
        normalized_email = email.lower()
        user = self.repo.get_by_email(normalized_email)

        if not user or not verify_password(password, user.hashed_password):
            raise BusinessException(
                message="Invalid email or password",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        token = create_access_token({"sub": str(user.id)})
        return token, user
