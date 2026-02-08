# app/services/user_service.py

from fastapi import status

from app.api.schemas.user_schema import UserBaseResponse, UserResponse
from app.common.exceptions import BusinessException
from app.models.db_user import DbUser
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def _to_user_response(self, user: DbUser) -> UserResponse:
        return UserResponse.model_validate(user)

    def _to_user_base_response(self, user: DbUser) -> UserBaseResponse:
        return UserBaseResponse.model_validate(user)

    def get_user_by_id(self, user_id: int) -> UserBaseResponse:
        user = self.repo.get_user(user_id=user_id)
        if not user:
            raise BusinessException(
                message="User not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return self._to_user_base_response(user)

    def get_user_model_by_id(self, user_id: int) -> DbUser:
        user = self.repo.get_user(user_id=user_id)
        if not user:
            raise BusinessException(
                message="User not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return user

    def get_all_users(self) -> list[UserResponse]:
        users = self.repo.get_all_users()
        return [self._to_user_response(user) for user in users]

    def update_current_user_profile(
        self,
        current_user: DbUser,
        first_name: str,
        last_name: str,
    ) -> UserBaseResponse:
        current_user.first_name = first_name
        current_user.last_name = last_name
        user = self.repo.update_user(current_user)
        return self._to_user_base_response(user)

    def partially_update_current_user_profile(
        self,
        current_user: DbUser,
        data: dict,
    ) -> UserBaseResponse:
        if "first_name" in data and data["first_name"]:
            current_user.first_name = data["first_name"]
        if "last_name" in data and data["last_name"]:
            current_user.last_name = data["last_name"]
        user = self.repo.update_user(current_user)
        return self._to_user_base_response(user)
