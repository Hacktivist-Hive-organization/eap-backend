# app/repositories/request_subtype_repository.py
from sqlalchemy.orm import Session
from app.models import DBRequestSubtype

class RequestSubtypeRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id_and_type(self, subtype_id: int, type_id: int):
        return self.db.query(DBRequestSubtype).filter(
            DBRequestSubtype.id == subtype_id,
            DBRequestSubtype.type_id == type_id
        ).first()

    def get_all(self):
        return self.db.query(DBRequestSubtype).all()
