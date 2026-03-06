# user_repository.py

from sqlalchemy.orm import Session

from app.models.db_user import DbUser


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, user_id: int):
        user = self.db.query(DbUser).filter(DbUser.id == user_id).first()  # type: ignore
        return user

    def get_all_users(self):
        return self.db.query(DbUser).all()

    def get_by_email(self, email: str):
        return self.db.query(DbUser).filter(DbUser.email == email).first()  # type: ignore

    def create(
        self,
        email: str,
        hashed_password: str,
        first_name: str,
        last_name: str,
        is_email_verified: bool = False,
    ) -> DbUser:
        user = DbUser(
            email=email,  # type: ignore
            hashed_password=hashed_password,  # type: ignore
            first_name=first_name,  # type: ignore
            last_name=last_name,  # type: ignore
            is_active=True,  # type: ignore
            is_email_verified=is_email_verified,  # type: ignore
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_user(self, user: DbUser) -> DbUser:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
