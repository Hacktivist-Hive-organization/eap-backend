# app/services/user_service.py

from fastapi import status

from app.common.enums import UserRole
from app.common.exceptions import BusinessException
from app.common.security_models import CurrentUser
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

    def get_user_by_id_for_requester_or_admin(
        self, user_id: int, current_user: CurrentUser
    ) -> DbUser:
        if current_user.role != UserRole.ADMIN and current_user.id != user_id:
            raise BusinessException(
                message="You do not have permission to access this user",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return self.get_user_by_id(user_id)

    def get_all_users(self) -> list[DbUser]:
        return self.repo.get_all_users()

    def _update_user_fields(
        self,
        user: DbUser,
        data: dict,
        allowed_fields: set[str],
        required_fields: set[str] | None = None,
    ) -> DbUser:
        required_fields = required_fields or set()

        for key, value in data.items():
            if key not in allowed_fields:
                continue

            if isinstance(value, str):
                value = value.strip()  # <-- обрезаем пробелы

            if key in required_fields and (
                value is None or (isinstance(value, str) and not value)
            ):
                raise BusinessException(
                    message=f"{key} cannot be empty",
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                )

            setattr(user, key, value)

        return self.repo.update_user(user)

    def current_user_update_profile(
        self, current_user: CurrentUser, data: dict
    ) -> DbUser:
        user = self.repo.get_user(current_user.id)
        if not user:
            raise BusinessException(
                message="User not found", status_code=status.HTTP_404_NOT_FOUND
            )

        allowed_fields = {"first_name", "last_name", "is_out_of_office"}
        required_fields = {"first_name", "last_name"}

        return self._update_user_fields(user, data, allowed_fields, required_fields)

    def admin_update_profile(
        self, user_id: int, data: dict, current_user: CurrentUser
    ) -> DbUser:
        user = self.repo.get_user(user_id=user_id)
        if not user:
            raise BusinessException(
                message="User not found",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if (
            current_user.id == user_id
            and data.get("role") is not None
            and data["role"] != UserRole.ADMIN
        ):
            raise BusinessException(
                message="Cannot downgrade own admin",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        allowed_fields = {
            "first_name",
            "last_name",
            "is_out_of_office",
            "role",
            "is_active",
        }
        required_fields = {"first_name", "last_name"}

        return self._update_user_fields(user, data, allowed_fields, required_fields)
