from app.common.exceptions import (InvalidCredentials, UserAlreadyExists,
                                   UserNotFound)
from app.common.security import (create_access_token, hash_password,
                                 validate_password, verify_password)
from app.models.db_user import DbUser
from app.repositories.user_repository import UserRepository


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
        return self.repo.create(email=normalized_email, hashed_password=hashed_password)

    def login(self, email: str, password: str) -> str:
        normalized_email = email.lower()
        user = self.repo.get_by_email(normalized_email)

        if not user or not verify_password(password, user.hashed_password):
            raise InvalidCredentials()

        return create_access_token({"sub": str(user.id)})
