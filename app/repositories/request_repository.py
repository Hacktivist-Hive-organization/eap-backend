# app/repositories/request_repository.py
from sqlalchemy.orm import Session
from app.models import DBRequest


class RequestRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, request: DBRequest):
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        return request