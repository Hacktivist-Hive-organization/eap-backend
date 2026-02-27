# app/repositories/request_repository.py

from typing import List, Optional

from sqlalchemy.orm import Session, selectinload

from app.common.enums import Status
from app.models import DBRequest


class RequestRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        request: DBRequest,
        current_user_id: int,
        current_status: Optional[Status] = Status.DRAFT,
    ):
        db_request = DBRequest(
            type_id=request.type_id,
            subtype_id=request.subtype_id,
            title=request.title,
            description=request.description,
            business_justification=request.business_justification,
            priority=request.priority,
            current_status=current_status,
            requester_id=current_user_id,
        )
        self.db.add(db_request)
        self.db.commit()
        self.db.refresh(db_request)
        return db_request

    def get_requests_by_user(self, user_id: int, statuses: List[Status]):
        query = self.db.query(DBRequest).filter(DBRequest.requester_id == user_id)
        if statuses:
            query = query.filter(DBRequest.current_status.in_(statuses))
        return query.order_by(DBRequest.updated_at.desc()).all()

    def get_request_details(self, request_id: int):
        return (
            self.db.query(DBRequest)
            .options(
                selectinload(DBRequest.requester),
                selectinload(DBRequest.type),
                selectinload(DBRequest.subtype),
                selectinload(DBRequest.req_tracking),
            )
            .filter(DBRequest.id == request_id)
            .first()
        )

    def is_request_owned_by_user(self, request_id: int, user_id: int) -> bool:
        return (
            self.db.query(DBRequest.id)
            .filter(DBRequest.id == request_id, DBRequest.requester_id == user_id)
            .first()
            is not None
        )

    def update_request_status(self, request, status: Status, commit: bool = True):
        request.current_status = status
        if commit:
            self.db.commit()
            self.db.refresh(request)
        return request

    def save(self, request: DBRequest) -> DBRequest:
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        return request
