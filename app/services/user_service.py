from app.common.exceptions import (
    UserNotFound,
    UserAlreadyExists,
    InvalidCredentials
)
from app.repositories.user_repository import UserRepository
from app.models.db_user import DbUser
from app.common.security import (
    hash_password,
    verify_password,
    create_access_token,
    validate_password,
)


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def get_user_by_id(self, user_id: int) -> DbUser | None:
        user = self.repo.get_user(user_id=user_id)
        if not user:
            raise UserNotFound()
        return user

    def get_all_users(self) -> list[DbUser]:
        return self.repo.get_all_users()

    def register(self, email: str, password: str) -> DbUser:
        normalized_email = email.lower()

        if self.repo.get_by_email(normalized_email):
            raise UserAlreadyExists()

        validate_password(password)
        hashed_password = hash_password(password)
        return self.repo.create(email=email, hashed_password=hashed_password)

    def login(self, email: str, password: str) -> str:
        normalized_email = email.lower()
        user = self.repo.get_by_email(normalized_email)

        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentials()

        return create_access_token({"sub": str(user.id)})
