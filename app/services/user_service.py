# app/services/user_service.py

from fastapi import status

from app.common.exceptions import BusinessException
from app.models.db_user import DbUser
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def get_user_by_id(self, user_id: int) -> DbUser:
        user = self.repo.get_user(user_id=user_id)
        if not user:
            raise BusinessException(
                message="User not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return user

    def get_user_model_by_id(self, user_id: int) -> DbUser:
        user = self.repo.get_user(user_id=user_id)
        if not user:
            raise BusinessException(
                message="User not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return user

    def get_all_users(self) -> list[DbUser]:
        return self.repo.get_all_users()

    def update_current_user_profile(
        self,
        current_user: DbUser,
        first_name: str,
        last_name: str,
    ) -> DbUser:
        current_user.first_name = first_name
        current_user.last_name = last_name
        return self.repo.update_user(current_user)

    def partially_update_current_user_profile(
        self,
        current_user: DbUser,
        data: dict,
    ) -> DbUser:
        if "first_name" in data and data["first_name"]:
            current_user.first_name = data["first_name"]
        if "last_name" in data and data["last_name"]:
            current_user.last_name = data["last_name"]
        return self.repo.update_user(current_user)
