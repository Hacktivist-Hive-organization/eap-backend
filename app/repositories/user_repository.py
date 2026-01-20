from sqlalchemy.orm import Session
from app.models.db_user import DbUser


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: int):
        user = self.db.query(DbUser).filter(DbUser.id == user_id).first()
        return user

    def get_all_users(self):
        return self.db.query(DbUser).all()

    def get_by_email(self, email: str):
        return self.db.query(DbUser).filter(DbUser.email == email).first()

    def create(self, email: str, hashed_password: str) -> DbUser:
        user = DbUser(
            email=email,
            hashed_password=hashed_password,
            is_active=True,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
