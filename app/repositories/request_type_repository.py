# app/repositories/request_type_repository.py
from sqlalchemy.orm import Session
from app.models import DBRequestType

class RequestTypeRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, type_id: int):
        return self.db.query(DBRequestType).filter_by(id=type_id).first()