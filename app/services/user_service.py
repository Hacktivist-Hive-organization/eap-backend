from fastapi import status

from app.common.exceptions import BusinessException

# from app.common.security import create_access_token, hash_password, verify_password
# from app.common.utils import (
#     is_email_valid,
#     is_password_strong,
#     is_required_fields_filled,
# )
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

    #
    # def register(
    #     self, email: str, password: str, first_name: str, last_name: str
    # ) -> tuple[str, "DbUser"]:
    #
    #     normalized_email = email.strip().lower()
    #
    #     checks = [
    #         {
    #             "func": lambda: is_required_fields_filled(
    #                 email=normalized_email,
    #                 password=password,
    #                 first_name=first_name,
    #                 last_name=last_name,
    #             ),
    #             "message": "All required fields must be filled",
    #             "status": status.HTTP_422_UNPROCESSABLE_CONTENT,
    #         },
    #         {
    #             "func": lambda: is_email_valid(normalized_email),
    #             "message": "Invalid email or password",
    #             "status": status.HTTP_422_UNPROCESSABLE_CONTENT,
    #         },
    #         {
    #             "func": lambda: not self.repo.get_by_email(normalized_email),
    #             "message": "User already exists",
    #             "status": status.HTTP_409_CONFLICT,
    #         },
    #         {
    #             "func": lambda: is_password_strong(password),
    #             "message": "Password is too weak",
    #             "status": status.HTTP_422_UNPROCESSABLE_CONTENT,
    #         },
    #     ]
    #
    #     for check in checks:
    #         if not check["func"]():
    #             raise BusinessException(
    #                 message=check["message"],
    #                 status_code=check["status"],
    #             )
    #
    #     hashed_password = hash_password(password)
    #
    #     user = self.repo.create(
    #         email=normalized_email,
    #         hashed_password=hashed_password,
    #         first_name=first_name,
    #         last_name=last_name,
    #     )
    #
    #     token = create_access_token({"sub": str(user.id)})
    #     return token, user
    #
    # def login(self, email: str, password: str) -> tuple[str, DbUser]:
    #
    #     normalized_email = email.strip().lower()
    #
    #     if not is_email_valid(normalized_email):
    #         raise BusinessException(
    #             message="Invalid email or password",
    #             status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    #         )
    #
    #     user = self.repo.get_by_email(normalized_email)
    #
    #     if not user or not verify_password(password, user.hashed_password):
    #         raise BusinessException(
    #             message="Invalid email or password",
    #             status_code=status.HTTP_401_UNAUTHORIZED,
    #         )
    #
    #     token = create_access_token({"sub": str(user.id)})
    #     return token, user
