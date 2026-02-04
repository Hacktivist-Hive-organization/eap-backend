# app/services/user_service.py

from fastapi import status

from app.common.exceptions import BusinessException
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
