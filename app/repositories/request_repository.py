# app/repositories/request_repository.py
from typing import List

from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload
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
            requester_id=request.requester_id,
        )
        self.db.add(db_request)
        self.db.commit()
        self.db.refresh(db_request)
        return db_request

    def get_requests_by_user(self, user_id: int, statuses: List[str]):
        query = self.db.query(DBRequest).filter(DBRequest.requester_id == user_id)
        if statuses:
            query = query.filter(DBRequest.status.in_(statuses))
        return query.order_by(DBRequest.created_at.desc()).all()

    def get_request_details(self, request_id: int):
        return (
            self.db.query(DBRequest)
            .options(
                selectinload(DBRequest.requester),
                selectinload(DBRequest.type),
                selectinload(DBRequest.subtype),
            )
            .filter(DBRequest.id == request_id)
            .first()
        )
