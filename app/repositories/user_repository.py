from sqlalchemy.orm import Session
from app.models.db_user import DbUser

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self ,user_id: int):
        user = self.db.query(DbUser).filter(DbUser.id == user_id).first()
        return user

