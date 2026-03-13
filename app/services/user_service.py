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

    def get_all_users(self) -> list[DbUser]:
        return self.repo.get_all_users()

    def partially_update_current_user_profile(
        self,
        user_id: int,
        data: dict,
    ) -> DbUser:
        user = self.repo.get_user(user_id=user_id)
        if not user:
            raise BusinessException(
                message="User not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if "first_name" in data:
            user.first_name = data["first_name"]

        if "last_name" in data:
            user.last_name = data["last_name"]

        if "is_out_of_office" in data:
            user.is_out_of_office = data["is_out_of_office"]

        return self.repo.update_user(user)
