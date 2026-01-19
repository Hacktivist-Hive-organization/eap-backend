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

    def get_user_by_id(self, user_id: int) -> DbUser:
        user = self.repo.get_user(user_id=user_id)
        if not user:
            raise ValueError("User not found")
        return user

    def get_all_users(self):
        return self.repo.get_all_users()

    def register(self, email: str, password: str) -> DbUser:
        if self.repo.get_by_email(email):
            raise ValueError("User already exists")

        validate_password(password)
        hashed_password = hash_password(password)
        return self.repo.create(email=email, hashed_password=hashed_password)

    def login(self, email: str, password: str) -> str:
        user = self.repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise ValueError("Invalid credentials")

        return create_access_token({"sub": str(user.id)})
