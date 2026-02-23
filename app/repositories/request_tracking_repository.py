from sqlalchemy.orm import Session

from app.common.enums import Status
from app.models import DBRequestTracking


class RequestTrackingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, comment: str, request_id: int, status: Status, user_id: int):
        db_request_tracking = DBRequestTracking(
            comment= comment,
            request_id= request_id,
            status= status,
            user_id= user_id,
        )
        self.db.add(db_request_tracking)
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

