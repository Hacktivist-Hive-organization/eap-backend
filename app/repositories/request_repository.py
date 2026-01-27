# app/repositories/request_repository.py
from sqlalchemy.orm import Session

from app.common.enums import Status
from app.models import DBRequest


class RequestRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, request: DBRequest):
        db_request = DBRequest(
            type_id=request.type_id,
            subtype_id=request.subtype_id,
            title=request.title,
            description=request.description,
            business_justification=request.business_justification,
            priority=request.priority,
            status=Status.DRAFT,
        )
        self.db.add(db_request)
        self.db.commit()
        self.db.refresh(db_request)
        return db_request
