from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.common.enums import Status
from app.models import DBRequest, DBRequestTracking


class RequestTrackingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        comment: str,
        request_id: int,
        status: Status,
        user_id: int,
        commit: bool = True,
    ):
        db_request_tracking = DBRequestTracking(
            comment=comment,
            request_id=request_id,
            status=status,
            user_id=user_id,
        )
        self.db.add(db_request_tracking)
        if commit:
            self.db.commit()
            self.db.refresh(db_request_tracking)
        return db_request_tracking

    def get_request_tracking_by_request_id(self, request_id: int):
        query = self.db.query(DBRequestTracking).filter(
            DBRequestTracking.request_id == request_id
        )
        request_tracking = query.order_by(DBRequestTracking.created_at.desc()).all()
        return request_tracking

    def get_tracking_by_request_user_id(self, request_id: int, user_id: int):
        return (
            self.db.query(DBRequestTracking)
            .filter(
                DBRequestTracking.request_id == request_id,
                DBRequestTracking.user_id == user_id,
            )
            .order_by(DBRequestTracking.created_at.desc())
            .first()
        )

    def get_requests_for_approver(
        self, approver_id: int, statuses: Optional[List[Status]] = None
    ) -> list[DBRequest]:
        """
        Returns all requests assigned to the approver via tracking entries,
        optionally filtered by request statuses.
        """
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
            stmt = stmt.where(DBRequest.current_status.in_(statuses))

        return self.db.execute(stmt).scalars().all()
