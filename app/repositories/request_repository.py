# app/repositories/request_repository.py
from sqlalchemy.orm import Session

from app.models import DBRequest
from app.common.enums import Status


class RequestRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, request: DBRequest):
        db_request = DBRequest(
            type_id= request.type_id,
            subtype_id= request.subtype_id,
            title= request.title,
            description= request.description,
            business_justification= request.business_justification,
            priority= request.priority,
            status= Status.DRAFT,
            requester_id = request.requester_id
        )
        self.db.add(db_request)
        self.db.commit()
        self.db.refresh(db_request)
        return db_request

    def get_requests_by_user(self, user_id: int, status: str):
        return (self.db.query(DBRequest).filter(DBRequest.requester_id == user_id,
                                                DBRequest.status == status)
                .order_by(DBRequest.created_at.desc())
                .all()
                )