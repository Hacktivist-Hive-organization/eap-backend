from app.models import DbUser
from app.repositories import UserRepository


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def get_userinfo(self, user_id: int | None = None) -> DbUser:
        user = self.repo.get_user(user_id=user_id)
        return user
