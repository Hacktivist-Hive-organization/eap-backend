from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


class HealthRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_health(self):
        try:
            self.db.execute(text("SELECT 1"))
            db_status = "connected"
        except SQLAlchemyError:
            db_status = "disconnected"
        return db_status
