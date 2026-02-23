from sqlalchemy.orm import Session

from app.common.enums import Status
from app.models import DBRequestTracking


class RequestTrackingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_request_tracking_by_request_id(self, request_id: int):
        query = self.db.query(DBRequestTracking).filter(
            DBRequestTracking.request_id == request_id
        )
        request_tracking = query.order_by(DBRequestTracking.created_at.desc()).all()
        return request_tracking

    def create_tracking_entry(
        self,
        request_id: int,
        user_id: int,
        approver_id: int | None,
        status: Status,
        comment: str,
    ) -> DBRequestTracking:

        tracking = DBRequestTracking(
            request_id=request_id,
            user_id=user_id,
            approver_id=approver_id,
            status=status,
            comment=comment,
        )

        self.db.add(tracking)
        self.db.commit()
        self.db.refresh(tracking)

        return tracking
