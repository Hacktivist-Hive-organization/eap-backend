from sqlalchemy.orm import Session

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
