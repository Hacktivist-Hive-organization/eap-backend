# app/repositories/request_repository.py

from typing import List, Optional, cast

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.common.enums import Status
from app.models import DBRequest, DBRequestTracking


class RequestRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        request: DBRequest,
        current_user_id: int,
        current_status: Optional[Status] = Status.DRAFT,
    ) -> DBRequest:
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

    def get_all_requests(self) -> List[DBRequest]:
        query = self.db.query(DBRequest).filter(
            DBRequest.current_status != Status.DRAFT.value
        )
        return cast(List[DBRequest], query.order_by(DBRequest.updated_at.desc()).all())

    def get_requests_by_statuses(self, statuses: List[Status]) -> List[DBRequest]:
        query = self.db.query(DBRequest).filter(
            DBRequest.current_status.in_([s.value for s in statuses])
        )
        return cast(List[DBRequest], query.order_by(DBRequest.updated_at.desc()).all())

    def get_requests_by_user(
        self, user_id: int, statuses: Optional[List[Status]] = None
    ) -> List[DBRequest]:
        query = self.db.query(DBRequest).filter(DBRequest.requester_id == user_id)
        if statuses:
            query = query.filter(
                DBRequest.current_status.in_([s.value for s in statuses])
            )
        return cast(List[DBRequest], query.order_by(DBRequest.updated_at.desc()).all())

    def get_request_details(self, request_id: int) -> Optional[DBRequest]:
        return cast(
            Optional[DBRequest],
            self.db.query(DBRequest)
            .options(
                selectinload(DBRequest.requester),
                selectinload(DBRequest.type),
                selectinload(DBRequest.subtype),
                selectinload(DBRequest.req_tracking),
            )
            .filter(DBRequest.id == request_id)
            .first(),
        )

    def is_request_owned_by_user(self, request_id: int, user_id: int) -> bool:
        return (
            self.db.query(DBRequest.id)
            .filter(DBRequest.id == request_id, DBRequest.requester_id == user_id)
            .first()
            is not None
        )

    def update_request_status(
        self, request: DBRequest, status: Status, commit: bool = True
    ) -> DBRequest:
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

    def get_requests_by_assignee_and_status(
        self, approver_id: int, statuses: Optional[List[Status]] = None
    ) -> List[DBRequest]:
        stmt = (
            select(DBRequest)
            .join(DBRequestTracking)
            .where(DBRequestTracking.user_id == approver_id)
            .distinct()
            .options(
                selectinload(DBRequest.requester),
                selectinload(DBRequest.type),
                selectinload(DBRequest.subtype),
                selectinload(DBRequest.req_tracking),
            )
            .order_by(DBRequest.updated_at.asc())
        )

        if statuses:
            stmt = stmt.where(DBRequest.current_status.in_([s.value for s in statuses]))

        return cast(List[DBRequest], self.db.execute(stmt).scalars().all())
